import { getProvider } from '../llm';
import { LLMProvider, ChatMessage } from '../llm/BaseProvider';
import { WorkerAgent } from './WorkerAgent';
import fs from 'node:fs';
import path from 'node:path';
import { readMemoryContext } from '../memory';
import { PersonaShell } from './PersonaShell';

export class ManagerAgent {
    private llm: LLMProvider;
    public cancelRequested: boolean = false;

    constructor() {
        this.llm = getProvider();
    }

    /** Signal the agent to stop at the next safe checkpoint */
    cancel() {
        this.cancelRequested = true;
        console.log('[Manager] ⛔ Cancel requested — will stop at next safe checkpoint.');
    }

    /** Reset cancel flag for the next request */
    private resetCancel() {
        this.cancelRequested = false;
    }

    /**
     * Compress a worker result into a compact summary for inter-step context.
     * Preserves URLs, numbers, table headers, and key findings.
     * Avoids an extra LLM call by using intelligent truncation.
     */
    private compactResult(result: string, maxLen: number = 600): string {
        if (result.length <= maxLen) return result;

        // Extract and preserve URLs
        const urls = result.match(/https?:\/\/[^\s)]+/g) || [];
        const urlBlock = urls.length > 0 ? `\nURLs: ${urls.slice(0, 5).join(', ')}` : '';

        // Extract and preserve table headers (first row of markdown tables)
        const tableHeaders = result.match(/\|[^\n]+\|/g);
        const headerLine = tableHeaders && tableHeaders.length > 0 ? `\nTable: ${tableHeaders[0]}` : '';

        // Take the first and last portions, preserving boundaries
        const headBudget = Math.floor((maxLen - urlBlock.length - headerLine.length) * 0.6);
        const tailBudget = maxLen - headBudget - urlBlock.length - headerLine.length - 30;

        const head = result.substring(0, headBudget);
        const tail = tailBudget > 50 ? result.substring(result.length - tailBudget) : '';

        return `${head}\n...[COMPACTED ${result.length - maxLen} chars]...\n${tail}${urlBlock}${headerLine}`;
    }

    async processUserRequest(prompt: string, imagesBase64: string[] = []): Promise<string> {
        this.resetCancel(); // Clear any previous cancel flag
        console.log(`\n[Manager] Analyzing request: "${prompt}"`);
        const agentPersona = process.env.AGENT_PERSONA || "You are a helpful multi-agent assistant designed to write excellent code and utilize terminals.";

        // Build dynamic agent catalog
        let agentCapabilities = "\n\n[AVAILABLE WORKER AGENTS]\nThe following agents are ALREADY registered and running in this system. You MUST delegate tasks to these existing agents ONLY. DO NOT invent new role names.\n";
        const existingRoles: string[] = [];
        try {
            const agentsDir = path.join(process.cwd(), 'workspace', 'agents');
            if (fs.existsSync(agentsDir)) {
                const agentFolders = fs.readdirSync(agentsDir).filter(f => fs.statSync(path.join(agentsDir, f)).isDirectory());
                for (const agentId of agentFolders) {
                    if (agentId === 'manager') continue;
                    const shell = new PersonaShell(agentId);
                    const caps = shell.getCapabilities();
                    if (caps.status === 'stopped') continue; // Prevent delegating to offline agents
                    if (!caps.role && !caps.name) continue; // Skip empty/broken agent folders
                    const roleName = caps.role || agentId;
                    existingRoles.push(roleName);
                    const toolsList = caps.allowedTools || caps.tools || [];
                    const toolsStr = Array.isArray(toolsList) && toolsList.length > 0 ? toolsList.join(', ') : 'general';
                    const descStr = caps.description ? ` — ${caps.description}` : '';
                    agentCapabilities += `- "${roleName}" (${caps.name || agentId}): ${toolsStr}${descStr}\n`;
                }
            }

            const skillsDir = path.join(process.cwd(), 'skills');
            if (fs.existsSync(skillsDir)) {
                const files = fs.readdirSync(skillsDir).filter(f => f.endsWith('.json') && f !== 'package.json');
                if (files.length > 0) {
                    agentCapabilities += "\nSkills: ";
                    const skillNames: string[] = [];
                    for (const file of files) {
                        try {
                            const metadata = JSON.parse(fs.readFileSync(path.join(skillsDir, file), 'utf-8'));
                            skillNames.push(metadata.name || file.replace('.json', ''));
                        } catch (e) { }
                    }
                    agentCapabilities += skillNames.join(', ') + '\n';
                }
            }
        } catch (e) { console.error("Could not load agent catalog."); }

        const persona = new PersonaShell('manager');
        const compiledPersonaPrompt = persona.compileSystemPrompt();

        // Skip memory context for cron-triggered requests to prevent cross-contamination
        // between concurrent cron jobs (e.g. baseball agent seeing Iran conflict context)
        const isCronTriggered = prompt.includes('[SYSTEM CRON TRIGGER]') || prompt.includes('[SYSTEM MANUAL TRIGGER]');
        const memorySection = isCronTriggered ? '' : `\n\n[MEMORY CONTEXT]\n${readMemoryContext()}`;

        // Inject a compact summary of active cron jobs (names only, no full prompts)
        let cronJobsSection = "";
        try {
            const cronPath = path.join(process.cwd(), 'workspace', 'cron_jobs.json');
            if (fs.existsSync(cronPath)) {
                const jobs = JSON.parse(fs.readFileSync(cronPath, 'utf-8'));
                const enabledJobs = jobs.filter((j: any) => j.status !== 'disabled');
                if (enabledJobs.length > 0) {
                    cronJobsSection = "\n\n[ACTIVE CRON JOBS] " + enabledJobs.map((j: any) =>
                        `${j.name || j.description}${j.preferredTime ? ` @${j.preferredTime}` : ` every ${j.intervalHours}h`}`
                    ).join(', ');
                }
            }
        } catch (e) { }

        const systemPrompt = `${compiledPersonaPrompt}\n\n[SYSTEM CONTEXT]\nCurrent Local Time: ${new Date().toLocaleString()}\nTimezone Name: ${Intl.DateTimeFormat().resolvedOptions().timeZone}${memorySection}${cronJobsSection}\n\n[TASK INSTRUCTIONS]
Your job is to break down the user's complex request into a sequential plan of sub-tasks.
Each sub-task MUST be assigned to one of the EXISTING Worker Agents listed above. Use their exact Role name (e.g. "${existingRoles[0] || 'Researcher'}", "${existingRoles[1] || 'Coder'}").
CRITICAL: DO NOT invent new agent roles! If a task doesn't perfectly match any agent, assign it to the closest matching existing agent. The Coder agent is your general-purpose workhorse for any file/script/implementation work.
${agentCapabilities}

[SCHEDULING CAPABILITY]
You CAN schedule recurring tasks! Your Worker Agents have a "schedule_task" tool that creates OR updates cron jobs.
When the user asks you to do something on a schedule (daily, hourly, weekly, etc.), include a step that tells the worker to use schedule_task.
Examples of requests you SHOULD schedule (NOT refuse):
- "Send me weather every morning at 5 AM" → schedule_task with command "preferredTime:05:00"
- "Check my email every hour" → schedule_task with command "1" (interval in hours)
- "Remind me about X every week" → schedule_task with command "168"
CRITICAL UPDATE RULE: If the user says "update", "change", "modify", or "edit" an existing cron job, tell the Worker to use schedule_task with the EXACT SAME "filename" (job name) as the existing job. The system will automatically update it in place instead of creating a new one. Never create a new job when the user explicitly wants to modify an existing one.
FORBIDDEN ACTION: NEVER instruct a worker to write a Python script (e.g. update_cron.py) or bash script to modify workspace/cron_jobs.json manually. You MUST ALWAYS use the native schedule_task tool. Manual python scripting of cron jobs causes memory corruption.
The scheduler runs on a 60-second heartbeat and will auto-execute the task via the Manager Agent.
NEVER tell the user you cannot schedule tasks. You absolutely can.

If the user is simply saying hello, asking a meta question about you (e.g. "who are you", "what can you do"), or making small talk that requires NO external data, DO NOT generate a plan. Instead, use the 'direct_response' field to reply strictly in character as your Persona without delegating any subtasks.
CRITICAL DELEGATION RULE: If the user asks you to browse, search, look up, check, find, research, open a website, or requests ANY real-time information (weather, news, prices, scores, events, current data) — you MUST ALWAYS delegate to a Worker agent. NEVER use direct_response for these. You do NOT have real-time data access — only Worker agents can browse the web, run scripts, and fetch live information. When in doubt, DELEGATE rather than respond directly.
IMPORTANT: The user is texting you directly on WhatsApp right now! You DO NOT need any external tools, APIs (like Twilio or Meta), or skills to reply to them. Any string you place into the 'direct_response' field will be instantly routed straight back to their WhatsApp chat natively.
CRITICAL CRON RULE: If this request contains "[SYSTEM CRON TRIGGER]" or "[SYSTEM MANUAL TRIGGER]", you MUST ALWAYS generate a plan with Worker tasks. NEVER use the 'direct_response' field for cron/scheduled tasks! The reason is: only Worker Agents have access to tools like send_whatsapp, send_email, browse_web, etc. If you use direct_response, no tools will be executed and no messages will be delivered. Always delegate cron tasks to the Coder worker agent.
When using the 'direct_response' field, ALWAYS format your output to be user-friendly. Use WhatsApp flavored markdown and clean tables for structural data.
CRITICAL JSON TRUNCATION RULE: The backend API has a hard limit of 1500 output tokens. If your response exceeds this length, it will be forcefully clipped, causing a fatal JSON parse crash. Keep your generated "plan" steps reasonably concise. HOWEVER, DO NOT instruct your delegated Worker Agents to be concise. You MUST command them to return the most highly detailed, comprehensive markdown tables possible when scraping data.

[IMAGE / DESIGN / CANVA ROUTING RULE]
If the user asks to create, generate, or design any image, graphic, poster, social media post, video, or visual content — you MUST ALWAYS delegate this to the Canva Design & Creation Expert agent. NEVER use direct_response to refuse or explain limitations. NEVER route image/design tasks to Browser Specialist. The Canva agent has specialized tools (canva_generate_image, canva_generate_video, canva_list_templates) and its own API keys. Let the specialized agent handle the request and figure out the best approach — do NOT make assumptions about what APIs can or cannot do.

[STOCK / MARKET / FINANCE ROUTING RULE]
If the user asks about stocks, stock market, market analysis, stock prices, market movers, gainers, losers, portfolio, earnings, technical analysis, fundamental analysis, S&P 500, NASDAQ, Dow Jones, tickers, or ANY financial market topic — you MUST ALWAYS delegate this to the "Sentinel" agent (Stock Exchange Analyst). NEVER route stock/market tasks to "MLB Fantasy Analyst" or "Fantasy Baseball Strategist" even if both mention "market" or "analyst" in their names. Sentinel has 8 specialized skills (stock_quote, stock_screener, stock_compare, market_movers, earnings_calendar, stock_news, portfolio_tracker, Stock Market Analysis). For daily market reports and cron triggers involving market data, ALWAYS assign the role as "Sentinel" or "Stock Exchange Analyst".

[FORMULA 1 / F1 ROUTING RULE]
If the user asks about Formula 1, F1, Grand Prix, race predictions, pole position, qualifying, tire strategy, pit stops, DRS, F1 standings, championship, constructors, any F1 driver (Verstappen, Hamilton, Leclerc, Norris, etc.), any F1 team (Red Bull, Ferrari, McLaren, Mercedes, etc.), or ANY motorsport/racing topic — you MUST ALWAYS delegate this to the "Pitwall" agent (Formula 1 Race Strategist & Analyst). Pitwall has 8 specialized skills (f1_race_predictor, f1_qualifying_analysis, f1_track_intelligence, f1_driver_form, f1_weather_strategy, f1_tire_strategy, f1_championship_tracker, f1_race_briefing). Always assign the role as "Pitwall" or "Formula 1 Race Strategist".

[LINKEDIN / PERSONAL BRANDING ROUTING RULE]
If the user asks to write, draft, create, post, publish, or schedule a LinkedIn post, OR asks about LinkedIn content strategy, personal branding on LinkedIn, LinkedIn engagement tips, LinkedIn hashtags, or ANY LinkedIn-related content creation — you MUST ALWAYS delegate this to the "Pulse" agent (LinkedIn Content Strategist & Personal Brand Architect). Pulse has the linkedin_post skill and specializes in crafting viral, high-engagement LinkedIn content. Always assign the role as "Pulse" or "LinkedIn Content Strategist". CRITICAL: Pulse will ALWAYS get user approval before publishing — never skip the approval step.

[VOICE MESSAGE REPLY RULE]
If the user's request contains "[SYSTEM: The user sent a voice message", you MUST create EXACTLY ONE task that handles everything (research, processing, AND sending the voice reply). DO NOT create separate tasks for research and voice reply — this causes duplicate voice messages. Assign the single task to the agent best suited for the research portion, and instruct that agent to ALSO send the result as a voice note using the send_voice tool. Example: if they ask about weather, assign ONE task to the Researcher that says "Look up the weather AND send the result as a voice note using send_voice."

[WHATSAPP NATIVE FEATURES]
If the user is asking a question that requires multiple choices, or you want to survey them, you can output a native WhatsApp Poll anywhere in your response using the tags: \`[POLL]Question|Option A|Option B|Option C[/POLL]\`. WhatsApp allows a max of 12 options. You can also utilize this when asking the user for context or how they wish to proceed.
If the user asks to send a message to a WhatsApp group or to multiple people, YOU CAN DO THIS! Instruct your delegated Worker to use the "send_whatsapp" tool and set the "to" field to the exact name of the WhatsApp group or a comma-separated list of phone numbers. Do not tell the user it is not supported natively.

Analyze the prompt and return a JSON object.
A step can either be:
1. "task": A standard sequential step executed by a single agent.
2. "parallel": A block of independent subtasks that can be executed concurrently by multiple agents. Use "parallel" whenever possible for independent data gathering or I/O fetching.

Example input: "Scrape the front page of hackernews and save the top 5 titles to titles.txt. Also find the weather in Tokyo."
Example output:
{
  "plan": [
    {
      "type": "parallel",
      "name": "Initial Data Gathering",
      "subtasks": [
        {
          "role": "Web Scraper",
          "instruction": "Write a python script using requests and beautifulsoup to scrape news.ycombinator.com and extract the top 5 titles."
        },
        {
          "role": "Information Fetcher",
          "instruction": "Find the current weather in Tokyo."
        }
      ]
    },
    {
      "type": "task",
      "role": "File Writer",
      "instruction": "Take the titles provided by the Web Scraper and the weather data and save them all to a summary file named output.txt."
    }
  ]
}
`;

        let userContent: string | any[] = Object.keys(prompt).length ? prompt : prompt;
        // Wrap the payload in an attention-grabbing header so the LLM knows what to focus on instead of hallucinating based on the Memory Log
        if (typeof userContent === 'string') {
            userContent = `[ACTIVE LIVE USER REQUEST]\n${userContent}`;
        }

        if (imagesBase64.length > 0) {
            userContent = [{ type: 'text', text: typeof userContent === 'string' ? userContent : JSON.stringify(userContent) }];
            for (const img of imagesBase64) {
                userContent.push({ type: 'image_url', image_url: { url: img } });
            }
        }

        const messages: ChatMessage[] = [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userContent }
        ];

        try {
            let planResult: {
                direct_response?: string;
                plan?: Array<{
                    type: "task" | "parallel";
                    name?: string;
                    role?: string;
                    instruction?: string;
                    subtasks?: Array<{ role: string; instruction: string }>;
                }>
            } | null = null;
            const maxLoops = 5;

            for (let i = 0; i < maxLoops; i++) {
                try {
                    planResult = await this.llm.generateStructuredOutputs<{
                        direct_response?: string;
                        plan?: Array<{
                            type: "task" | "parallel";
                            name?: string;
                            role?: string;
                            instruction?: string;
                            subtasks?: Array<{ role: string; instruction: string }>;
                        }>
                    }>(messages, {
                        type: "object",
                        properties: {
                            direct_response: { type: "string", description: "Use this ONLY for direct conversational replies without creating a plan." },
                            plan: {
                                type: "array",
                                items: {
                                    type: "object",
                                    properties: {
                                        type: { type: "string" },
                                        name: { type: "string" },
                                        role: { type: "string" },
                                        instruction: { type: "string" },
                                        subtasks: {
                                            type: "array",
                                            items: {
                                                type: "object",
                                                properties: {
                                                    role: { type: "string" },
                                                    instruction: { type: "string" }
                                                },
                                                required: ["role", "instruction"]
                                            }
                                        }
                                    },
                                    required: ["type"]
                                }
                            }
                        }
                    }, 'manager');
                    break; // Success!
                } catch (e: any) {
                    // Don't retry API/infrastructure errors (rate limits, auth, network) as "JSON parse errors"
                    // — only genuine JSON validation failures should trigger the LLM self-healing loop.
                    const errMsg = e.message || '';
                    if (errMsg.includes('Rate limit') || errMsg.includes('429') || errMsg.includes('401') || errMsg.includes('503') || errMsg.includes('UNAUTHENTICATED') || errMsg.includes('Internal IDE API Error')) {
                        console.error(`[Manager] API Error (not a JSON issue) — aborting self-healing loop: ${errMsg.substring(0, 200)}`);
                        throw e;
                    }
                    console.warn(`\n⚠️ [Manager] JSON Parse Error. Requesting LLM Self-Healing...`);
                    messages.push({ role: 'user', content: `SYSTEM EXCEPTION: You generated an invalid JSON payload that crashed the parser (${errMsg.substring(0, 300)}). Please strictly evaluate your JSON syntax, ensure all internal quotes are escaped, and try again.` });
                    if (i === maxLoops - 1) throw e;
                }
            }

            if (!planResult) {
                return "Error: Failed to generate a valid plan after maximum retries.";
            }

            if (planResult.direct_response) {
                // CODE-LEVEL SAFEGUARD: Some models (e.g. GPT-4o) ignore prompt-level delegation rules
                // and use direct_response for tasks that require real-time data or browsing.
                // Detect this and force delegation to a Worker agent.
                const lowerPrompt = prompt.toLowerCase();
                const requiresDelegation = [
                    'browse', 'search', 'look up', 'check', 'find', 'research', 'open a browser', 'open browser',
                    'weather', 'news', 'price', 'score', 'stock', 'current', 'latest', 'today',
                    'what is happening', 'what happened', 'send ', 'post ', 'create ', 'generate ',
                    'schedule', 'email', 'whatsapp', 'voice'
                ].some(keyword => lowerPrompt.includes(keyword));

                if (requiresDelegation) {
                    console.log(`[Manager] ⚠️ LLM used direct_response for a task requiring delegation. Overriding to Worker plan.`);
                    // Override: create a simple plan delegating to the default coder agent
                    delete planResult.direct_response;
                    planResult.plan = [{
                        type: 'task' as const,
                        role: 'coder',
                        instruction: prompt
                    }];
                } else {
                    console.log(`[Manager] Direct Response generated.`);
                    return planResult.direct_response;
                }
            }

            if (!planResult.plan) {
                return "Error: No plan or direct response generated.";
            }

            console.log(`[Manager] Generated Plan with ${planResult.plan.length} top-level steps.`);

            console.log(JSON.stringify({ type: 'agent_flow', event: 'plan_generated', plan: planResult }));

            // Execute passing context along
            let globalContext: string[] = [`Original User Request: ${prompt}`];
            let finalOutput = "";

            for (let i = 0; i < planResult.plan.length; i++) {
                const step = planResult.plan[i];
                if (!step) continue;

                // Check for user-requested cancellation
                if (this.cancelRequested) {
                    console.log('[Manager] ⛔ Execution cancelled by user before step', i + 1);
                    return '⛔ Task cancelled by user.';
                }

                if (step.type === 'task' && step.role && step.instruction) {
                    const taskId = `${i + 1}`;
                    console.log(`\n[Manager] Delegating Task ${taskId}/${planResult.plan.length} to ${step.role}...`);

                    console.log(JSON.stringify({
                        type: 'agent_flow',
                        event: 'task_start',
                        taskId: taskId,
                        role: step.role,
                        instruction: step.instruction
                    }));

                    const resolvedRole = this.resolveRole(step.role, existingRoles);
                    const worker = new WorkerAgent(this.llm, resolvedRole, () => this.cancelRequested);
                    const result = await worker.executeTask(step.instruction, globalContext);

                    console.log(`[Manager] Task ${taskId} completed. Result:\n${result}\n`);

                    console.log(JSON.stringify({
                        type: 'agent_flow',
                        event: 'task_complete',
                        taskId: taskId,
                        result: result
                    }));

                    // Compact result to prevent unbounded context growth in multi-step plans
                    const compacted = this.compactResult(result);
                    globalContext.push(`Task ${taskId} (${step.role}): ${compacted}`);
                    finalOutput = result;

                } else if (step.type === 'parallel' && step.subtasks) {
                    console.log(`\n[Manager] Delegating Parallel Block ${i + 1}/${planResult.plan.length}: ${step.name}...`);

                    const promises = step.subtasks.map(async (subtask, j) => {
                        const taskId = `${i + 1}-${j + 1}`;
                        console.log(JSON.stringify({
                            type: 'agent_flow',
                            event: 'task_start',
                            taskId: taskId,
                            role: subtask.role,
                            instruction: subtask.instruction
                        }));

                        // Parallel tasks get a copy of the CURRENT global context!
                        const workerContext = [...globalContext];
                        const resolvedRole = this.resolveRole(subtask.role, existingRoles);
                        const worker = new WorkerAgent(this.llm, resolvedRole, () => this.cancelRequested);
                        const result = await worker.executeTask(subtask.instruction, workerContext);

                        console.log(`[Manager] Parallel Task ${taskId} completed.`);
                        console.log(JSON.stringify({
                            type: 'agent_flow',
                            event: 'task_complete',
                            taskId: taskId,
                            result: result
                        }));

                        return `${subtask.role}: ${result}`;
                    });

                    const parallelResults = await Promise.all(promises);
                    // Compact parallel results before pushing to context
                    const compactedParallel = parallelResults.map(r => this.compactResult(r)).join('\n---\n');
                    globalContext.push(`Parallel Block '${step.name}': ${compactedParallel}`);
                    finalOutput = parallelResults.join('\n\n');
                }
            }

            return `Plan execution finished successfully. Final Output:\n${finalOutput}`;

        } catch (e: any) {
            console.error("[Manager] Error generating/executing plan:", e);
            return `Failed to execute request: ${e.message}`;
        }
    }

    /**
     * Resolve an LLM-generated role name to an existing agent.
     * Prevents GPT-4o from creating phantom agents with suffixed names
     * like "browser-specialist-hx82l" instead of "Browser Specialist".
     */
    private resolveRole(generatedRole: string, existingRoles: string[]): string {
        if (!existingRoles.length) return generatedRole;

        const gen = generatedRole.toLowerCase().replace(/[-_]/g, ' ');

        // Exact match (case-insensitive)
        const exact = existingRoles.find(r => r.toLowerCase() === gen);
        if (exact) return exact;

        // Bidirectional substring match
        const substringMatch = existingRoles.find(r => {
            const existing = r.toLowerCase().replace(/[-_]/g, ' ');
            return existing.includes(gen) || gen.includes(existing);
        });
        if (substringMatch) return substringMatch;

        // Word overlap scoring: pick the role with the most shared words
        const genWords = gen.split(/\s+/).filter(w => w.length > 2);
        let bestMatch = '';
        let bestScore = 0;

        for (const role of existingRoles) {
            const roleWords = role.toLowerCase().replace(/[-_]/g, ' ').split(/\s+/).filter(w => w.length > 2);
            const overlap = genWords.filter(w => roleWords.some(rw => rw.includes(w) || w.includes(rw))).length;
            const score = overlap / Math.max(genWords.length, 1);
            if (score > bestScore) {
                bestScore = score;
                bestMatch = role;
            }
        }

        // Require at least 50% word overlap to accept a match
        if (bestScore >= 0.5 && bestMatch) {
            if (bestMatch.toLowerCase() !== generatedRole.toLowerCase()) {
                console.log(`[Manager] Role resolved: "${generatedRole}" → "${bestMatch}"`);
            }
            return bestMatch;
        }

        // Fallback: use the generated role as-is (will create a generic worker)
        console.warn(`[Manager] ⚠️ No matching agent for role "${generatedRole}". Using as generic worker.`);
        return generatedRole;
    }
}

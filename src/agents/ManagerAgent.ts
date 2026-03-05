import { getProvider } from '../llm';
import { LLMProvider, ChatMessage } from '../llm/BaseProvider';
import { WorkerAgent } from './WorkerAgent';
import fs from 'node:fs';
import path from 'node:path';
import { readMemoryContext } from '../memory';
import { PersonaShell } from './PersonaShell';

export class ManagerAgent {
    private llm: LLMProvider;

    constructor() {
        this.llm = getProvider();
    }

    async processUserRequest(prompt: string, imagesBase64: string[] = []): Promise<string> {
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
                    const identityStr = shell.getIdentity().split('\\n').filter(l => l.trim().length > 0)[0] || "Specialized Sub-Agent";
                    const roleName = caps.role || agentId;
                    existingRoles.push(roleName);
                    agentCapabilities += `- Agent ID: "${agentId}" | Role: "${roleName}" | Name: ${caps.name || agentId}\n  Summary: ${identityStr}\n  Tools: ${caps.allowedTools?.join(', ') || 'none'}\n`;
                }
            }

            const skillsDir = path.join(process.cwd(), 'skills');
            if (fs.existsSync(skillsDir)) {
                agentCapabilities += "\nAvailable Skill Summaries:\n";
                const files = fs.readdirSync(skillsDir).filter(f => f.endsWith('.json') && f !== 'package.json');
                for (const file of files) {
                    try {
                        const metadata = JSON.parse(fs.readFileSync(path.join(skillsDir, file), 'utf-8'));
                        agentCapabilities += `- ${metadata.name}: ${metadata.description}\n`;
                    } catch (e) { }
                }
            }
        } catch (e) { console.error("Could not load agent catalog."); }

        const persona = new PersonaShell('manager');
        const compiledPersonaPrompt = persona.compileSystemPrompt();

        // Skip memory context for cron-triggered requests to prevent cross-contamination
        // between concurrent cron jobs (e.g. baseball agent seeing Iran conflict context)
        const isCronTriggered = prompt.includes('[SYSTEM CRON TRIGGER]') || prompt.includes('[SYSTEM MANUAL TRIGGER]');
        const memorySection = isCronTriggered ? '' : `\n\n[MEMORY CONTEXT]\n${readMemoryContext()}`;

        const systemPrompt = `${compiledPersonaPrompt}\n\n[SYSTEM CONTEXT]\nCurrent Local Time: ${new Date().toLocaleString()}\nTimezone Name: ${Intl.DateTimeFormat().resolvedOptions().timeZone}${memorySection}\n\n[TASK INSTRUCTIONS]
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
The scheduler runs on a 60-second heartbeat and will auto-execute the task via the Manager Agent.
NEVER tell the user you cannot schedule tasks. You absolutely can.

If the user is simply saying hello, asking a basic question about you, or making small talk, DO NOT generate a plan. Instead, use the 'direct_response' field to reply strictly in character as your Persona without delegating any subtasks.
IMPORTANT: The user is texting you directly on WhatsApp right now! You DO NOT need any external tools, APIs (like Twilio or Meta), or skills to reply to them. Any string you place into the 'direct_response' field will be instantly routed straight back to their WhatsApp chat natively.
CRITICAL CRON RULE: If this request contains "[SYSTEM CRON TRIGGER]" or "[SYSTEM MANUAL TRIGGER]", you MUST ALWAYS generate a plan with Worker tasks. NEVER use the 'direct_response' field for cron/scheduled tasks! The reason is: only Worker Agents have access to tools like send_whatsapp, send_email, browse_web, etc. If you use direct_response, no tools will be executed and no messages will be delivered. Always delegate cron tasks to the Coder worker agent.
When using the 'direct_response' field, ALWAYS format your output to be user-friendly. Use WhatsApp flavored markdown and clean tables for structural data.
CRITICAL JSON TRUNCATION RULE: The backend API has a hard limit of 1500 output tokens. If your response exceeds this length, it will be forcefully clipped, causing a fatal JSON parse crash. Keep your generated "plan" steps reasonably concise. HOWEVER, DO NOT instruct your delegated Worker Agents to be concise. You MUST command them to return the most highly detailed, comprehensive markdown tables possible when scraping data.

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
                    console.warn(`\n⚠️ [Manager] JSON Parse Error. Requesting LLM Self-Healing...`);
                    messages.push({ role: 'user', content: `SYSTEM EXCEPTION: You generated an invalid JSON payload that crashed the parser (${e.message}). Please strictly evaluate your JSON syntax, ensure all internal quotes are escaped, and try again.` });
                    if (i === maxLoops - 1) throw e;
                }
            }

            if (!planResult) {
                return "Error: Failed to generate a valid plan after maximum retries.";
            }

            if (planResult.direct_response) {
                console.log(`[Manager] Direct Response generated.`);
                return planResult.direct_response;
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

                    const worker = new WorkerAgent(this.llm, step.role);
                    const result = await worker.executeTask(step.instruction, globalContext);

                    console.log(`[Manager] Task ${taskId} completed. Result:\n${result}\n`);

                    console.log(JSON.stringify({
                        type: 'agent_flow',
                        event: 'task_complete',
                        taskId: taskId,
                        result: result
                    }));

                    globalContext.push(`Task ${taskId} Result from ${step.role}: ${result}`);
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
                        const worker = new WorkerAgent(this.llm, subtask.role);
                        const result = await worker.executeTask(subtask.instruction, workerContext);

                        console.log(`[Manager] Parallel Task ${taskId} completed.`);
                        console.log(JSON.stringify({
                            type: 'agent_flow',
                            event: 'task_complete',
                            taskId: taskId,
                            result: result
                        }));

                        return `Parallel Task ${taskId} Result from ${subtask.role}: ${result}`;
                    });

                    const parallelResults = await Promise.all(promises);
                    globalContext.push(`Parallel Block '${step.name}' Results:\n${parallelResults.join('\n\n')}`);
                    finalOutput = parallelResults.join('\n\n');
                }
            }

            return `Plan execution finished successfully. Final Output:\n${finalOutput}`;

        } catch (e: any) {
            console.error("[Manager] Error generating/executing plan:", e);
            return `Failed to execute request: ${e.message}`;
        }
    }
}

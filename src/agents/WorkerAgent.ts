import { LLMProvider, ChatMessage } from '../llm/BaseProvider';
import { DynamicExecutor } from '../tools/DynamicExecutor';
import { BrowserTool, BrowseAction } from '../browser/tool';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { PersonaShell } from './PersonaShell';
import { sendWhatsAppMessage, sendWhatsAppAudio, getParticipatingGroups } from '../whatsapp';
import { readJobsSync, writeJobsSync, withJobs, CronJob } from '../CronStore';

export class WorkerAgent {
    private llm: LLMProvider;
    private executor: DynamicExecutor;
    private browserTool: BrowserTool;
    private role: string;
    private cancelChecker: (() => boolean) | undefined;

    constructor(llm: LLMProvider, role: string, cancelChecker?: () => boolean) {
        this.llm = llm;
        this.executor = new DynamicExecutor();
        this.browserTool = new BrowserTool();
        this.role = role;
        this.cancelChecker = cancelChecker;
    }

    async executeTask(instruction: string, context: string[], imagesBase64: string[] = []): Promise<string> {
        await this.executor.initialize();

        // Look up this worker's capabilities
        let assignedSkillsContext = "";
        try {
            const agentsPath = path.join(process.cwd(), 'agents.json');
            if (fs.existsSync(agentsPath)) {
                const agents = JSON.parse(fs.readFileSync(agentsPath, 'utf-8'));
                // Attempt to find an agent profile that matches this role name (case insensitive)
                const workerProfile = agents.find((a: any) => a.role.toLowerCase().includes(this.role.toLowerCase()) || a.name.toLowerCase() === this.role.toLowerCase());

                if (workerProfile && workerProfile.skills && workerProfile.skills.length > 0) {
                    // Lazy loading: inject only skill names + filenames to save tokens.
                    // Full metadata is available via execute_script --help at runtime.
                    assignedSkillsContext = "\n\nYOUR ASSIGNED SKILLS:\nYou have these specialized Python scripts. Use `execute_script` with the filename to run them.\n";
                    const skillsDir = path.join(process.cwd(), 'skills');
                    for (const skill of workerProfile.skills) {
                        try {
                            const metadata = JSON.parse(fs.readFileSync(path.join(skillsDir, `${skill}.json`), 'utf-8'));
                            assignedSkillsContext += `- ${skill}.py — ${metadata.description || skill}\n`;
                        } catch (e) { }
                    }
                    assignedSkillsContext += "\nTo see full usage for any skill, run: execute_script with filename \"<skill>.py\" and args \"--help\"\n";
                }
            }
        } catch (e) { console.error("Could not load worker profile."); }

        const persona = new PersonaShell(this.role);
        const compiledPersonaPrompt = persona.compileSystemPrompt();

        // Inject email routing rules from dashboard config
        let emailRoutingContext = '';
        try {
            const emailConfigPath = path.join(process.cwd(), 'workspace', 'email_config.json');
            if (fs.existsSync(emailConfigPath)) {
                const emailConfig = JSON.parse(fs.readFileSync(emailConfigPath, 'utf-8'));
                const cronEmail = emailConfig.cronResultsTo;
                const vendorEmail = emailConfig.vendorEmailTo;
                if (cronEmail || vendorEmail) {
                    emailRoutingContext = `\n\n[EMAIL ROUTING RULES]\n`;
                    if (cronEmail) emailRoutingContext += `• Cron / Automated Report Emails (task results, briefings, market snapshots, etc.): ALWAYS send to ${cronEmail}.\n`;
                    if (vendorEmail) emailRoutingContext += `• Manual user requests to email a contractor, vendor, friend, or external party (when no explicit address is given): default to ${vendorEmail}.\n`;
                    emailRoutingContext += `These are the ONLY addresses you should use when no other explicit recipient is given in the task.`;
                }
            }
        } catch (e) { }

        const systemPrompt = `${compiledPersonaPrompt}

[CURRENT DATE & TIME]
Today is: ${new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })} at ${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}.
CRITICAL: This date/time comes from the host server's real-time clock and is CORRECT. Do NOT doubt, question, "correct", or override this date under ANY circumstances. Do NOT suggest the user's date might be wrong or that the "actual date" is something else. Your training data cutoff is irrelevant — the system clock is the single source of truth.
${emailRoutingContext}

[TASK INSTRUCTIONS]
Your Role: ${this.role}
You have the ability to write scripts (Python, Node.js, Bash) and execute them to solve the user's task.
If you need a package, write a script that installs it or ask to run npm install.
Your goal is to complete the task autonomously and return the final result.
CRITICAL TOKEN RULE: Do not print massive HTML dumps. Use Python to parse, summarize, and extract ONLY the exact data you need. Your tool output context is truncated to 3000 characters.
CRITICAL JSON TRUNCATION RULE: The backend API has a hard limit of 1500 output tokens. If your response exceeds this length, it will be forcefully clipped, causing a fatal JSON parse crash. You MUST keep your 'thought' string under 500 words and be concise in your intermediate steps to prevent array string truncation!
CRITICAL MACOS PRIVACY RULE: NEVER run commands to search, list, or read files in \`~/Desktop\`, \`~/Documents\`, or \`~/Downloads\` as this will trigger a strict macOS GUI permission dialog that blocks the backend. You must ONLY work within the current project directory \`${process.cwd()}\`.
CRITICAL COMPLETION RULE: You start with 30 steps. Your budget auto-extends if you are making progress (up to 300 max). ALWAYS output final_answer as soon as you have enough information. For research tasks (finding businesses, data, lists), write final_answer after 3-5 sources — do NOT keep browsing trying to be exhaustive. Partial results delivered are ALWAYS better than a perfect answer never delivered. If a website fails to load after 2 attempts, move on immediately.
${assignedSkillsContext}

Available tools you can request in your JSON response:
- run_command: { "command": "echo hello" } (Run a bash command within the project environment)
- write_script: { "filename": "test.py", "content": "print('hello')" } (Write a code script to disk)
- execute_script: { "filename": "test.py", "args": "" } (Execute a dynamically written script)
- browse_web: Open a REAL browser. ALWAYS prefer this over Python scripts for web searches.
  To use browse_web, set "command" to the sub-action and use other fields:
    - Navigate: { "action": "browse_web", "command": "navigate", "filename": "https://google.com" }
    - Click:    { "action": "browse_web", "command": "click", "args": "button.submit" }
    - Type:     { "action": "browse_web", "command": "type", "args": "input[name=q]", "content": "search query" }
    - Read:     { "action": "browse_web", "command": "read_content" }  ← reads full page (capped at 1500 chars)
    - Read targeted section: { "action": "browse_web", "command": "read_content", "args": "main" }  ← CSS selector for focused extraction. Use this when you need specific data (e.g. "args": ".results", "args": "article", "args": "#contact", "args": "table"). PREFER targeted selectors over full-page reads to save tokens.
    - Scroll:   { "action": "browse_web", "command": "scroll", "args": "down" }
    - List:     { "action": "browse_web", "command": "list_elements" }  ← shows all clickable links/buttons with their text. Use this when you can't find what to click.
    - Run JS:   { "action": "browse_web", "command": "execute_js", "content": "return document.querySelector('.score').innerText" }  ← run custom JS to extract specific data
    - Close:    { "action": "browse_web", "command": "close" }
- wait_for_user: { "message": "Please log in to your account" } (Pause and ask the user to do something in the browser, like logging in. Waits up to 120 seconds.)
- schedule_task: { "command": "24", "content": "Fetch Vancouver WA weather and send to user via WhatsApp", "filename": "Daily Weather Brief" } (Schedule OR UPDATE a recurring task. If a job with the same "filename" already exists it will be UPDATED in place — use this when the user asks to change/modify an existing job. To create or update an interval-based job: "command" = interval in hours (e.g. "24"). To create or update a time-of-day job (runs once daily at a fixed time): "command" = "preferredTime:HH:MM" (e.g. "preferredTime:07:00"). "content" = the prompt/task to execute, "filename" = short name for the job (must match exactly to update).)
- message_agent: { "target": "Role Name", "message": "Text to send" } (Delegate a sub-task to a specialized sub-agent)
- send_email: { "to": "user@example.com", "subject": "Hello", "body": "My message here" } (Send an outbound email natively using OAuth.)
- read_emails: { "content": "query string", "target": "5" } (Scan the user's Gmail inbox natively. "content" is the search query like 'is:unread' or 'from:boss', and "target" is the max number of results.)
- send_whatsapp: { "message": "Hello!", "to": "Engineering Team" } (Send a WhatsApp message. "to" is optional – if omitted, the message goes to the default configured owner. You can provide a comma-separated list of phone numbers, the word "default", OR the exact name of a WhatsApp Group the bot is in. CRITICAL: the "message" field is the exact text that the human user will read. Do NOT put internal status logs like 'Message sent successfully' in here. Write the conversational answer.)
- send_voice: { "message": "Hello, how are you?", "args": "voice_id" } (Send a voice note to the user via WhatsApp. The text in "message" will be converted to speech using ElevenLabs TTS and delivered as an audio message. Use "args" to optionally specify a voice ID. Available voices:
  • "21m00Tcm4TlvDq8ikWAM" = Rachel (default, warm female)
  • "EXAVITQu4vr4xnSDxMaL" = Bella (soft female)
  • "ErXwobaYiN019PkySvjV" = Antoni (calm male)
  • "VR6AewLTigWG4xSOukaG" = Arnold (deep male)
  • "pNInz6obpgDQGcFmaJgB" = Adam (confident male)
- update_whatsapp_whitelist: { "command": "add_dm", "target": "+14155552671" } (Safely grant or revoke WhatsApp access for users. "command" can be "add_dm", "remove_dm", "add_group", or "remove_group". "target" should be the raw phone number (e.g. +14155552671) or exact Group JID strings.)
- final_answer: { "result": "The final output" } (CRITICAL: You MUST include the 'result' key containing your answer)

BROWSER USAGE GUIDELINES:
- ALWAYS prefer browse_web over writing Python scripts for web searches, data lookup, or scraping. The browser is faster and uses fewer tokens.
- The browser uses a Chrome Relay with the user's REAL logged-in browser session. The user is ALREADY authenticated on most sites. NEVER ask the user to log in.

SMART BROWSING STRATEGY (follow this pattern for ANY site):
1. Navigate to the site URL
2. Read the page content to see what's visible
3. Identify clickable links/buttons FROM THE TEXT you just read (look for team names, menu items, tab labels)
4. Click the most relevant link using its EXACT VISIBLE TEXT — e.g., if you see "Market Makers" in the content, click "Market Makers"
5. Read the resulting page
6. If you found what you need, extract data and deliver final_answer
7. If not, repeat steps 3-5 with a different link

FALLBACK STRATEGY (use when clicks fail or you can't find links):
- If a click fails, use list_elements to see all clickable items on the page, then click the right one by exact text.
- If the page is too complex, use execute_js to extract specific data directly: e.g. "return document.querySelector('.player-name').innerText"
- If you can't find the data after 3 click attempts, try a Google search to find it on a different website.

KEY RULES:
- After reading content, ALWAYS look for clickable items IN THE TEXT and click them by their exact visible text.
- When you see a team name, league name, or any relevant link text in the page content, CLICK IT immediately.
- Do NOT construct complex CSS selectors — just use the text you see on the page.
- Do NOT use jQuery syntax like :contains(). Just pass the plain text: "args": "Players"
- If a click fails, try slight variations of the text (e.g., "Player Rankings" instead of "Players").
- For Google searches: navigate to "https://www.google.com/search?q=your+query" then read_content.
- If a website's navigation is too complex after 5 click attempts, try web search instead to find the data on a different site.

PERSISTENCE RULES:
- You MUST go above and beyond to complete the task. Do NOT give up after one attempt.
- NEVER tell the user "please navigate to..." or "please click on..." — YOU click on it yourself.
- NEVER tell the user "please ensure you are logged in" — they ARE logged in.
- Your goal is to DELIVER RESULTS, not instructions to the user. The user hired you to do the work.

CRITICAL FORMATTING INSTRUCTION: 
When providing your \`final_answer\`, you MUST format the output to be highly readable and user-friendly. 
- ALWAYS use GitHub-flavored Markdown. 
- You MUST return the comprehensive, fully detailed list of your findings. DO NOT summarize or truncate the final result.
- If you are returning a list of items, data points, comparisons, or contractors, you MUST format it as a clean Markdown table with columns (e.g., Name, Website, Phone, Rating).
- Use bold text for emphasis and headers (##, ###) to separate sections logically.

Context from previous steps:
${context.join('\n')}
`;

        // Build user content — include images as multimodal content blocks if present
        let userContent: string | any[] = instruction;
        if (imagesBase64.length > 0) {
            userContent = [{ type: 'text', text: instruction }];
            for (const img of imagesBase64) {
                userContent.push({ type: 'image_url', image_url: { url: img } });
            }
        }

        let messages: ChatMessage[] = [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userContent }
        ];

        // ═══════════════════════════════════════════════════════════════
        // DYNAMIC STEP BUDGET SYSTEM
        // Instead of a fixed limit, the agent gets a base budget with
        // auto-extensions at checkpoints if it's making real progress.
        // ═══════════════════════════════════════════════════════════════
        const BASE_BUDGET = 50;           // Every task starts with 50 steps (browser tasks need more)
        const EXTENSION_GRANT = 30;       // Each extension adds 30 more steps
        const CHECKPOINT_WINDOW = 5;      // Warn 5 steps before current limit
        const HARD_CEILING = 300;         // Absolute max — never exceeded

        let currentBudget = BASE_BUDGET;
        let extensionsGranted = 0;
        const maxExtensions = Math.floor((HARD_CEILING - BASE_BUDGET) / EXTENSION_GRANT);

        // Stall detection state
        const visitedUrls = new Map<string, number>();  // URL → visit count
        let consecutiveErrors = 0;
        let lastSummary = '';
        let staleSummaryCount = 0;
        let checkpointInjected = false;
        let postCheckpointActions = 0;
        let postCheckpointHasWork = false;

        // Autonomy Loop
        for (let i = 0; i < HARD_CEILING; i++) {

            // Check for cancel at the top of every iteration
            if (this.cancelChecker && this.cancelChecker()) {
                console.log(`[Worker - ${this.role}] ⛔ Cancel detected at iteration ${i + 1}. Aborting task.`);
                return '⛔ Task cancelled by user.';
            }

            // --- Budget exceeded check ---
            if (i >= currentBudget) {
                console.warn(`[Worker - ${this.role}] Budget exhausted (${currentBudget} steps). Returning best-effort.`);
                break;
            }

            // --- Checkpoint: inject warning when approaching current budget ---
            if (!checkpointInjected && i >= currentBudget - CHECKPOINT_WINDOW) {
                checkpointInjected = true;
                postCheckpointActions = 0;
                postCheckpointHasWork = false;

                const canExtend = extensionsGranted < maxExtensions;
                if (canExtend) {
                    // Soft checkpoint — tell agent it can keep going if it has more to do
                    console.log(`[Worker - ${this.role}] 📋 Checkpoint at step ${i}/${currentBudget} (${extensionsGranted} extensions used)`);
                    messages.push({
                        role: 'user',
                        content: `⚠️ CHECKPOINT: You've used ${i} of your current ${currentBudget} step budget. If you have enough data, issue final_answer NOW. If you need more steps to complete the task properly, continue working — your budget will be extended automatically. Do NOT rush to a poor answer if more browsing would substantially improve the result.`
                    });
                } else {
                    // Hard limit — force wrap-up
                    console.warn(`[Worker - ${this.role}] ⚠️ Final budget warning at step ${i}/${currentBudget}. No more extensions available.`);
                    messages.push({
                        role: 'user',
                        content: `⚠️ SYSTEM: FINAL BUDGET WARNING — You are on step ${i} of ${currentBudget} (maximum reached, no more extensions). You MUST issue final_answer NOW with whatever results you have. Partial results are INFINITELY better than no result.`
                    });
                }
            }

            // --- Post-checkpoint: monitor next actions to decide extension ---
            if (checkpointInjected && postCheckpointActions > 0 && postCheckpointActions <= 3) {
                // After 3 post-checkpoint actions, decide whether to extend
                if (postCheckpointActions === 3) {
                    if (postCheckpointHasWork && extensionsGranted < maxExtensions) {
                        // Check stall indicators before granting
                        const isStalled = consecutiveErrors >= 6 || staleSummaryCount >= 8;
                        const isLooping = [...visitedUrls.values()].some(count => count >= 5);

                        if (isStalled || isLooping) {
                            console.warn(`[Worker - ${this.role}] 🔄 Extension DENIED — stall detected (errors: ${consecutiveErrors}, stale: ${staleSummaryCount}, looping: ${isLooping})`);
                            messages.push({
                                role: 'user',
                                content: `⚠️ SYSTEM: Your budget will NOT be extended — the system detected you may be stuck (${isLooping ? 'revisiting same URLs' : isStalled ? 'consecutive errors or no new findings' : 'unknown'}). Issue final_answer NOW with your current findings.`
                            });
                        } else {
                            // GRANT EXTENSION
                            extensionsGranted++;
                            currentBudget += EXTENSION_GRANT;
                            checkpointInjected = false; // Reset for next checkpoint
                            console.log(`[Worker - ${this.role}] ✅ Budget extended: +${EXTENSION_GRANT} → ${currentBudget} steps (extension ${extensionsGranted}/${maxExtensions})`);
                        }
                    }
                    // If no real work detected, budget stays — agent will hit the limit naturally
                }
            }
            let response;
            try {
                response = await this.llm.generateStructuredOutputs<{
                    action: 'run_command' | 'write_script' | 'execute_script' | 'browse_web' | 'wait_for_user' | 'schedule_task' | 'message_agent' | 'send_email' | 'read_emails' | 'send_whatsapp' | 'send_voice' | 'update_whatsapp_whitelist' | 'final_answer';
                    command?: string;
                    filename?: string;
                    content?: string;
                    args?: string;
                    target?: string;
                    message?: string;
                    to?: string;
                    subject?: string;
                    body?: string;
                    result?: string;
                    summary_of_findings: string;
                    thought: string;
                }>(messages, {
                    type: "object",
                    properties: {
                        action: { type: "string", enum: ["run_command", "write_script", "execute_script", "browse_web", "wait_for_user", "schedule_task", "message_agent", "send_email", "read_emails", "send_whatsapp", "send_voice", "update_whatsapp_whitelist", "final_answer"] },
                        thought: { type: "string" },
                        summary_of_findings: { type: "string", description: "A highly compressed, 1-2 sentence memory of what you learned in this step. Retained forever even if thoughts are pruned." },
                        command: { type: "string" },
                        filename: { type: "string" },
                        content: { type: "string" },
                        args: { type: "string" },
                        target: { type: "string" },
                        message: { type: "string" },
                        to: { type: "string", description: "Optional email address or phone number target." },
                        subject: { type: "string" },
                        body: { type: "string" },
                        result: { type: "string", description: "The final answer or result string when action is final_answer" },
                    },
                    required: ["action", "thought", "summary_of_findings"]
                }, this.role);
            } catch (e: any) {
                console.warn(`\n⚠️ [Worker - ${this.role}] JSON Parse Error. Requesting LLM Self-Healing...`);
                messages.push({ role: 'user', content: `SYSTEM EXCEPTION: You generated an invalid JSON payload that crashed the parser (${e.message}). Please strictly evaluate your JSON syntax, ensure all internal quotes are escaped, and try again.` });
                continue;
            }

            // Enforce schema completeness independently
            if (response.action === 'final_answer' && !response.result) {
                console.warn(`\n⚠️ [Worker - ${this.role}] Missing Result Error. Requesting LLM Self-Healing...`);
                messages.push({ role: 'user', content: `SYSTEM EXCEPTION: You selected action 'final_answer', but you completely failed to include the 'result' key in your JSON! You MUST re-output your JSON and explicitly include the full 'result' key containing your formatted markdown table.` });
                continue;
            }

            // Log the thought process (useful for the DB / Dashboard later)
            console.log(`[Worker - ${this.role}] Thought: ${(response.thought || '').substring(0, 200)}`);
            // MED-4: Do NOT log raw LLM response to console — it may contain user PII,
            // un-sanitized input data, or partial API key/credential content from tool outputs.

            // CRITICAL FIX: To prevent "This model does not support assistant message prefill" crashes on strict providers
            // We append previous actions as 'user' system logs rather than 'assistant' message prefills.
            messages.push({ role: 'user', content: `[PRIOR AGENT ACTION HISTORY]: \n${JSON.stringify(response)}` });

            if (response.action === 'final_answer') {
                return response.result || response.summary_of_findings || "Task completed without explicit result.";
            }

            let toolOutput = "";
            try {
                if (response.action === 'run_command' && response.command) {
                    console.log(`[Worker - ${this.role}] Running command: ${response.command}`);
                    const res = await this.executor.runCommand(response.command);
                    toolOutput = `stdout: ${res.stdout}\nstderr: ${res.stderr}\nerror: ${res.error || 'none'}`;
                } else if (response.action === 'write_script' && response.filename && (response.content || response.result)) {
                    const content = response.content || response.result;
                    console.log(`[Worker - ${this.role}] Writing script: ${response.filename}`);
                    toolOutput = await this.executor.writeScript(response.filename, content as string);
                } else if (response.action === 'execute_script' && response.filename) {
                    console.log(`[Worker - ${this.role}] Executing script: ${response.filename}`);
                    const res = await this.executor.executeScript(response.filename, response.args);
                    toolOutput = `stdout: ${res.stdout}\nstderr: ${res.stderr}\nerror: ${res.error || 'none'}`;
                } else if (response.action === 'message_agent' && response.target && response.message) {
                    console.log(`[Worker - ${this.role}] Delegating sub-task via message_agent to peer ${response.target}...`);
                    console.log(JSON.stringify({
                        type: 'agent_flow',
                        event: 'task_start',
                        taskId: `sub-${Date.now()}`,
                        role: response.target,
                        instruction: response.message
                    }));

                    // Recursively instantiate a Worker passing along the contextual dialogue
                    const subWorker = new WorkerAgent(this.llm, response.target);
                    const subWorkerContext = [...context, `Message from peer ${this.role}: ${response.message}`];
                    const subResult = await subWorker.executeTask(response.message, subWorkerContext);

                    toolOutput = `Response from ${response.target}:\n${subResult}`;
                } else if (response.action === 'browse_web') {
                    // command = sub-action (navigate/click/type/read_content/scroll/close/execute_js)
                    // filename = URL (for navigate)
                    // args = CSS selector (for click/type) or direction (for scroll)
                    // content = text to type, or raw script payload for execute_js
                    const subAction = (response.command || 'navigate') as BrowseAction['action'];
                    const browseAction: BrowseAction = {
                        action: subAction,
                        url: response.filename,
                        selector: response.args,
                        text: response.content,
                        script: response.content,
                        message: response.message,
                        direction: response.args as 'up' | 'down',
                    };
                    console.log(`[Worker - ${this.role}] Browser action: ${browseAction.action} ${browseAction.url || browseAction.selector || ''}`);
                    let rawBrowserOutput = await this.browserTool.execute(browseAction);
                    // SECURITY (V7): Sanitize web content to prevent prompt injection from malicious websites
                    if (subAction === 'read_content' || subAction === 'execute_js') {
                        rawBrowserOutput = rawBrowserOutput
                            .replace(/\[SYSTEM\]/gi, '[WEB]')
                            .replace(/\[ASSISTANT\]/gi, '[WEB]')
                            .replace(/\[USER\]/gi, '[WEB]')
                            .replace(/ignore previous instructions/gi, '[FILTERED]')
                            .replace(/ignore all previous/gi, '[FILTERED]')
                            .replace(/you are now/gi, '[FILTERED]')
                            .replace(/new instructions:/gi, '[FILTERED]')
                            .replace(/\x00/g, '');
                        toolOutput = `---BEGIN WEB CONTENT---\n${rawBrowserOutput}\n---END WEB CONTENT---`;
                    } else {
                        toolOutput = rawBrowserOutput;
                    }
                } else if (response.action === 'wait_for_user') {
                    const waitMessage = response.message || 'Please complete the required action in the browser.';
                    console.log(`[Worker - ${this.role}] Requesting user interaction: ${waitMessage}`);
                    toolOutput = await this.browserTool.execute({ action: 'wait_for_user', message: waitMessage });
                } else if (response.action === 'schedule_task') {
                    // command = interval in hours OR "preferredTime:HH:MM" for time-of-day scheduling
                    // content = the prompt, filename = job name (used as upsert key)
                    const rawCommand = (response.command || '24').trim();
                    const MIN_INTERVAL_HOURS = 0.25; // 15 minutes minimum to prevent LLM spam

                    // Parse preferredTime syntax: "preferredTime:07:00"
                    let preferredTime: string | undefined;
                    let intervalHours = 24;
                    const preferredTimeMatch = rawCommand.match(/^preferredTime:(\d{1,2}:\d{2})$/i);
                    if (preferredTimeMatch && preferredTimeMatch[1]) {
                        preferredTime = preferredTimeMatch[1];
                    } else {
                        const rawInterval = parseFloat(rawCommand);
                        intervalHours = (!rawInterval || rawInterval < MIN_INTERVAL_HOURS) ? 24 : rawInterval;
                    }

                    const taskPrompt = (response.content || response.message || '').substring(0, 2000);
                    const jobName = (response.filename || 'Scheduled Task').substring(0, 200);

                    if (!taskPrompt) {
                        toolOutput = 'Error: No task prompt provided for schedule_task. Provide the task description in the "content" field.';
                    } else {
                        try {
                            // Use mutex-protected withJobs() to prevent race conditions
                            // with the scheduler's 60s tick and dashboard edits
                            let result = '';
                            await withJobs((jobs: CronJob[]) => {
                                // Upsert: check for existing job with the same name (case-insensitive)
                                const existingIndex = jobs.findIndex(
                                    (j: any) => j.description.toLowerCase() === jobName.toLowerCase()
                                );

                                if (existingIndex !== -1) {
                                    // UPDATE existing job in-place
                                    const existing = jobs[existingIndex]!;
                                    existing.prompt = taskPrompt;
                                    existing.intervalHours = intervalHours;
                                    if (preferredTime) {
                                        existing.preferredTime = preferredTime;
                                    } else {
                                        delete existing.preferredTime; // Clear time-of-day if switching back to interval
                                    }
                                    const scheduleStr = preferredTime ? `daily at ${preferredTime}` : `every ${intervalHours}h`;
                                    console.log(`[Worker - ${this.role}] Updated existing cron job: "${jobName}" → ${scheduleStr}`);
                                    result = `✅ Successfully updated existing cron job!\n- Name: ${jobName}\n- Schedule: ${scheduleStr}\n- New Task: ${taskPrompt.substring(0, 100)}...\n- Status: ${existing.status || 'enabled'}\n- ID: ${existing.id}`;
                                } else {
                                    // CREATE new job (only if under the cap)
                                    // SECURITY: Cap at 20 jobs max even from agent-scheduled tasks
                                    if (jobs.length >= 20) {
                                        result = 'Error: Maximum of 20 cron jobs reached. Delete an existing job before scheduling a new one.';
                                    } else {
                                        const newJob: any = {
                                            id: 'cron-' + Math.random().toString(36).substr(2, 9),
                                            description: jobName,
                                            prompt: taskPrompt,
                                            intervalHours,
                                            lastRunTimestamp: 0, // Run on next heartbeat
                                            agentId: 'manager',
                                            status: 'enabled'
                                        };
                                        if (preferredTime) newJob.preferredTime = preferredTime;
                                        jobs.push(newJob);
                                        const scheduleStr = preferredTime ? `daily at ${preferredTime}` : `every ${intervalHours}h`;
                                        console.log(`[Worker - ${this.role}] Scheduled new recurring task: "${jobName}" ${scheduleStr}`);
                                        result = `✅ Successfully scheduled recurring task!\n- Name: ${jobName}\n- Schedule: ${scheduleStr}\n- Task: ${taskPrompt.substring(0, 100)}...\n- Status: Enabled\n- ID: ${newJob.id}`;
                                    }
                                }
                                return jobs;
                            });
                            toolOutput = result;
                        } catch (e: any) {
                            toolOutput = `Failed to schedule task: ${e.message}`;
                        }
                    }
                } else if (response.action === 'update_whatsapp_whitelist' && response.command && response.target) {
                    // SECURITY (V3): Human-in-the-loop guard — allowlist changes are QUEUED, not applied immediately.
                    // This prevents prompt injection attacks from modifying the allowlist without admin knowledge.
                    try {
                        const target = response.target.trim();
                        const command = response.command;
                        const validCommands = ['add_dm', 'remove_dm', 'add_group', 'remove_group'];
                        if (!validCommands.includes(command)) {
                            toolOutput = `Error: Invalid command "${command}". Valid: ${validCommands.join(', ')}`;
                        } else {
                            // Queue the change to a pending file for dashboard/admin review
                            const pendingPath = path.join(process.cwd(), 'workspace', 'pending_allowlist_changes.json');
                            let pending: any[] = [];
                            if (fs.existsSync(pendingPath)) {
                                try { pending = JSON.parse(fs.readFileSync(pendingPath, 'utf8')); } catch { pending = []; }
                            }
                            pending.push({
                                id: 'awl-' + Math.random().toString(36).substr(2, 9),
                                command,
                                target,
                                requestedBy: this.role,
                                requestedAt: new Date().toISOString(),
                                status: 'pending'
                            });
                            fs.writeFileSync(pendingPath, JSON.stringify(pending, null, 2));
                            console.log(`[Worker - ${this.role}] SECURITY: Allowlist change QUEUED (not applied): ${command} → ${target}`);

                            // Notify admin via WhatsApp
                            const ownerJid = process.env.OWNER_JID || process.env.WHATSAPP_OWNER_NUMBER;
                            if (ownerJid) {
                                try {
                                    await sendWhatsAppMessage(ownerJid.includes('@') ? ownerJid : `${ownerJid}@s.whatsapp.net`,
                                        `🔐 *Security Alert*\n\nAn agent requested a WhatsApp allowlist change:\n• Action: ${command}\n• Target: ${target}\n• Requested by: ${this.role}\n\n⚠️ This change was NOT applied automatically. Please review and approve via the Dashboard.`
                                    );
                                } catch { /* non-critical if notification fails */ }
                            }
                            toolOutput = `✅ Allowlist change request queued for admin review.\n- Action: ${command}\n- Target: ${target}\n\nFor security, allowlist modifications require manual admin approval via the Dashboard.`;
                        }
                    } catch (e: any) {
                        toolOutput = `Failed to queue allowlist change: ${e.message}`;
                    }
                } else if (response.action === 'send_email' && response.to && response.subject && response.body) {
                    console.log(`[Worker - ${this.role}] Dispatching email to ${response.to}...`);
                    try {
                        const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..', '..') : path.join(__dirname, '..', '..');
                        const pythonScript = path.join(rootDir, 'skills', 'send_email.py');

                        // SECURITY FIX (CRIT-2): Use spawnSync with argument array instead of execSync
                        // template string to completely eliminate shell injection risk.
                        const result = spawnSync('python3', [
                            pythonScript,
                            '--to', response.to,
                            '--subject', response.subject,
                            '--body', response.body
                        ], { timeout: 30000, encoding: 'utf-8' });

                        if (result.error) throw result.error;
                        if (result.status !== 0) throw new Error(result.stderr || 'python3 exited non-zero');
                        toolOutput = `Email sent successfully:\n${result.stdout}`;
                    } catch (e: any) {
                        toolOutput = `Failed to send email. Ensure OAuth is configured via 'openspider tools email setup'. Error: ${e.message}`;
                    }
                } else if (response.action === 'read_emails') {
                    console.log(`[Worker - ${this.role}] Scanning Gmail Inbox...`);
                    // Support optional search queries via args or content, and maxResults via target (stringified number)
                    const query = response.args || response.content || 'is:unread';
                    const maxResults = response.target ? parseInt(response.target, 10) : 5;

                    const scanResult = await require('../services/GmailService').GmailService.getInstance().readEmails({ query, maxResults });

                    if (!scanResult.success) {
                        toolOutput = `Failed to read emails: ${scanResult.error}. Ensure OAuth is configured via 'openspider tools email setup'.`;
                    } else if (!scanResult.emails || scanResult.emails.length === 0) {
                        toolOutput = `Inbox Scan Complete: No emails found matching query "${query}".`;
                    } else {
                        toolOutput = `Inbox Scan Complete. Found ${scanResult.emails.length} emails matching "${query}":\n\n`;
                        scanResult.emails.forEach((email: any, index: number) => {
                            toolOutput += `[${index + 1}] Date: ${email.date}\n    From: ${email.from}\n    Subject: ${email.subject}\n    Snippet: ${email.snippet}\n\n`;
                        });
                    }
                } else if (response.action === 'send_whatsapp' && response.message) {
                    console.log(`[Worker - ${this.role}] Sending WhatsApp message...`);
                    try {
                        let targetJids: string[] = [];

                        // Determine the user's default WhatsApp JID and group policies from the config
                        const configPath = path.join(process.cwd(), 'workspace', 'whatsapp_config.json');
                        let defaultJid = '';
                        let groupPolicy = 'disabled';
                        let allowedGroupJids: string[] = [];

                        if (fs.existsSync(configPath)) {
                            const waConfig = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
                            if (waConfig.allowedDMs && waConfig.allowedDMs.length > 0) {
                                const firstEntry = waConfig.allowedDMs[0];
                                const rawNumber = (typeof firstEntry === 'string' ? firstEntry : firstEntry.number || '').replace(/\D/g, '');
                                defaultJid = `${rawNumber}@s.whatsapp.net`;
                            }
                            if (waConfig.groupPolicy) groupPolicy = waConfig.groupPolicy;
                            if (waConfig.allowedGroups && Array.isArray(waConfig.allowedGroups)) {
                                allowedGroupJids = waConfig.allowedGroups.map((g: any) => g.jid);
                            }
                        }

                        // If the agent explicitly provided a 'to' string, parse it for numbers, keywords, or group names
                        if (response.to && response.to.trim().length > 0) {
                            // Fetch groups once just in case we need them
                            let participatingGroups: Array<{ id: string, subject: string }> = [];
                            try {
                                if (groupPolicy !== 'disabled') {
                                    const allGroups = await getParticipatingGroups();
                                    if (groupPolicy === 'allowlist') {
                                        participatingGroups = allGroups.filter((g: any) => allowedGroupJids.includes(g.id));
                                    } else {
                                        participatingGroups = allGroups; // open policy
                                    }
                                }
                            } catch (e) {
                                console.error('[Worker] Failed to fetch participating groups:', e);
                            }

                            // Split by commas or semicolons
                            const recipients = response.to.split(/[,;]/);
                            for (let r of recipients) {
                                r = r.trim();
                                if (!r) continue;
                                const lowerR = r.toLowerCase();

                                if (lowerR === 'me' || lowerR === 'default' || lowerR === 'owner' || lowerR === 'user') {
                                    if (defaultJid) targetJids.push(defaultJid);
                                } else if (r.trim().endsWith('@g.us') || r.trim().endsWith('@s.whatsapp.net')) {
                                    // Raw JID passthrough — support direct group/DM JIDs
                                    const cleanJid = r.trim();
                                    if (cleanJid.endsWith('@g.us')) {
                                        if (groupPolicy === 'disabled') {
                                            console.warn(`[Worker - ${this.role}] Warning: Group routing is disabled by policy. Skipping ${cleanJid}`);
                                        } else if (groupPolicy === 'allowlist' && !allowedGroupJids.includes(cleanJid)) {
                                            console.warn(`[Worker - ${this.role}] Warning: Group ${cleanJid} is not in the Allowlist. Skipping.`);
                                        } else {
                                            targetJids.push(cleanJid);
                                        }
                                    } else {
                                        targetJids.push(cleanJid);
                                    }
                                } else {
                                    // See if it has digits, treat as phone number
                                    const rawNumber = r.replace(/\D/g, '');
                                    if (rawNumber.length > 5 && /^\+?\d+$/.test(r.replace(/\s/g, ''))) {
                                        targetJids.push(`${rawNumber}@s.whatsapp.net`);
                                    } else {
                                        // Assume it's a group name — robust two-way case-insensitive match
                                        const cleanLowerR = lowerR.replace(/\bgroup\b/ig, '').trim();

                                        // PASS 1: Exact Match (Case Insensitive)
                                        let matchedGroup = participatingGroups.find(g => g.subject.toLowerCase() === lowerR || g.subject.toLowerCase() === cleanLowerR);

                                        // PASS 2: Fuzzy Match (Only if exact match fails)
                                        if (!matchedGroup) {
                                            const fuzzyMatches = participatingGroups.filter(g => {
                                                const sub = g.subject.toLowerCase();
                                                return sub.includes(lowerR) || lowerR.includes(sub) || (cleanLowerR.length >= 3 && sub.includes(cleanLowerR));
                                            });

                                            if (fuzzyMatches.length === 1) {
                                                matchedGroup = fuzzyMatches[0];
                                            } else if (fuzzyMatches.length > 1) {
                                                const options = fuzzyMatches.map(g => `"${g.subject}"`).join(', ');
                                                console.warn(`[Worker - ${this.role}] Warning: Group name "${r}" is ambiguous and matches multiple groups: ${options}`);
                                                // We intentionally do NOT define matchedGroup here; it will fall through to the warning block below and tell the agent it's ambiguous.
                                            }
                                        }

                                        if (matchedGroup) {
                                            targetJids.push(matchedGroup.id);
                                        } else {
                                            // Provide the agent with the exact list of available group names to prevent hallucination
                                            const availableGroups = participatingGroups.map(g => `"${g.subject}"`).join(', ');
                                            console.warn(`[Worker - ${this.role}] Warning: Could not resolve WhatsApp target "${r}" to a unique Group Name. Evaluated against ${participatingGroups.length} groups.`);
                                            // The agent will see this error injected into its context loop so it can ask for clarification
                                            targetJids.push(`ERROR_NOT_FOUND:${r}`);
                                        }
                                    }
                                }
                            }
                            // Also if the agent gave nothing extractable, try falling back
                            if (targetJids.length === 0 && defaultJid) {
                                targetJids.push(defaultJid);
                            }
                        } else {
                            if (defaultJid) targetJids.push(defaultJid);
                        }

                        // Remove duplicates
                        targetJids = [...new Set(targetJids)];

                        if (targetJids.length === 0) {
                            toolOutput = 'Error: No WhatsApp target resolved! Could not map "' + response.to + '" to a known group name or phone number. Add a phone number to allowedDMs or ensure the exact group name is used.';
                        } else if (targetJids.some(j => j.startsWith('ERROR_NOT_FOUND:'))) {
                            const errs = targetJids.filter(j => j.startsWith('ERROR_NOT_FOUND:')).map(j => j.split(':')[1]);
                            toolOutput = `Error: The requested WhatsApp target(s) [${errs.join(', ')}] were ambiguous or not found in the allowed group list. You MUST ask the user to clarify exactly which group they mean.`;
                        } else {
                            // Get agent persona name for the header
                            let agentName = 'OpenSpider';
                            try {
                                const persona = new PersonaShell('manager');
                                const caps = persona.getCapabilities();
                                if (caps && caps.name) agentName = caps.name;
                            } catch (e) { }

                            const formattedMsg = `✨ *${agentName}*\n\n${response.message}`;

                            let sentCount = 0;
                            const failedJids: string[] = [];
                            for (const jid of targetJids) {
                                try {
                                    await sendWhatsAppMessage(jid, formattedMsg);
                                    sentCount++;
                                } catch (e: any) {
                                    console.error(`Failed to send to ${jid}:`, e);
                                    failedJids.push(`${jid}: ${e.message}`);
                                }
                            }

                            if (failedJids.length > 0) {
                                toolOutput = `⚠️ Partial success or complete failure. Sent to ${sentCount} recipient(s). Failed to send to ${failedJids.length} recipient(s): \n${failedJids.join('\n')}`;
                            } else {
                                toolOutput = `✅ WhatsApp message sent successfully to ${sentCount} recipient(s): ${targetJids.join(', ')}.`;
                            }
                        }
                    } catch (e: any) {
                        toolOutput = `Failed to send WhatsApp message: ${e.message}`;
                    }
                } else if (response.action === 'send_voice' && response.message) {
                    console.log(`[Worker - ${this.role}] Generating voice message via ElevenLabs TTS...`);
                    try {
                        // Determine the user's WhatsApp JID from the config
                        const configPath = path.join(process.cwd(), 'workspace', 'whatsapp_config.json');
                        let userJid = '';
                        if (fs.existsSync(configPath)) {
                            const waConfig = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
                            if (waConfig.allowedDMs && waConfig.allowedDMs.length > 0) {
                                const firstEntry = waConfig.allowedDMs[0];
                                const rawNumber = (typeof firstEntry === 'string' ? firstEntry : firstEntry.number || '').replace(/\D/g, '');
                                userJid = `${rawNumber}@s.whatsapp.net`;
                            }
                        }
                        if (!userJid) {
                            toolOutput = 'Error: No WhatsApp user configured. Add a phone number to the allowedDMs list in Channels > WhatsApp config.';
                        } else {
                            const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..', '..') : path.join(__dirname, '..', '..');
                            const pythonScript = path.join(rootDir, 'skills', 'send_voice.py');

                            // SECURITY FIX (CRIT-2): Build args array for spawnSync — no shell interpretation.
                            // Read voice config: use agent-specified voice_id, or fall back to dashboard config
                            const spawnArgs = [pythonScript, '--text', response.message];
                            if (response.args) {
                                spawnArgs.push('--voice_id', response.args);
                            } else {
                                const voiceConfigPath = path.join(process.cwd(), 'workspace', 'voice_config.json');
                                if (fs.existsSync(voiceConfigPath)) {
                                    try {
                                        const voiceConfig = JSON.parse(fs.readFileSync(voiceConfigPath, 'utf-8'));
                                        if (voiceConfig.voiceId) { spawnArgs.push('--voice_id', voiceConfig.voiceId); }
                                    } catch (e) { }
                                }
                            }
                            const voiceResult = spawnSync('python3', spawnArgs, { timeout: 60000, encoding: 'utf-8' });
                            if (voiceResult.error) throw voiceResult.error;
                            if (voiceResult.status !== 0) throw new Error(voiceResult.stderr || 'send_voice.py exited non-zero');
                            const stdout = voiceResult.stdout;

                            // Extract audio file path from script output
                            const pathMatch = stdout.match(/AUDIO_FILE_PATH:(.+)/);
                            if (pathMatch && pathMatch[1]) {
                                const audioFilePath = pathMatch[1].trim();
                                await sendWhatsAppAudio(userJid, audioFilePath);

                                // Clean up temp audio file
                                try { fs.unlinkSync(audioFilePath); } catch (e) { }

                                // Get agent persona name
                                let agentName = 'OpenSpider';
                                try {
                                    const persona = new PersonaShell('manager');
                                    const caps = persona.getCapabilities();
                                    if (caps && caps.name) agentName = caps.name;
                                } catch (e) { }

                                toolOutput = `✅ Voice message sent successfully to ${userJid} via ElevenLabs TTS.`;
                            } else {
                                toolOutput = `Failed to generate voice message. Script output: ${stdout}`;
                            }
                        }
                    } catch (e: any) {
                        toolOutput = `Failed to send voice message: ${e.message}\n${e.stdout?.toString() || ''}\n${e.stderr?.toString() || ''}`;
                    }
                } else {
                    toolOutput = `Invalid action or missing parameters. You requested '${response.action}'. Check the schema. run_command needs 'command', write_script needs 'filename' and 'content', send_email needs 'to', 'subject', and 'body', send_whatsapp needs 'message'. You provided: ${JSON.stringify(response)}`;
                }
            } catch (e: any) {
                toolOutput = `Tool execution failed: ${e.message}`;
            }

            // [Token Optimization] Tool output cap: increased for relay browser content
            // which now prioritizes tables/data over nav chrome. The relay extracts up to
            // 10K chars, tool.ts passes up to 5K, so we keep 5K to preserve the data.
            const MAX_LENGTH = 5000;
            if (toolOutput.length > MAX_LENGTH) {
                const head = toolOutput.substring(0, 3500);
                const tail = toolOutput.substring(toolOutput.length - 1500);
                toolOutput = `${head}\n\n... [TRUNCATED ${toolOutput.length - MAX_LENGTH} characters. Write a script to parse/summarize if you need the full data] ...\n\n${tail}`;
            }

            console.log(`[Worker - ${this.role}] Tool Output: ${toolOutput.substring(0, 200)}...`);
            messages.push({ role: 'user', content: `Tool Result:\n${toolOutput}` });

            // ── Dynamic Budget: Stall Detection Instrumentation ──
            // Track URLs visited
            if (response.action === 'browse_web' && response.command === 'navigate' && response.filename) {
                const url = response.filename;
                visitedUrls.set(url, (visitedUrls.get(url) || 0) + 1);
            }

            // Track consecutive errors (but NOT relay click/read failures — those are normal browser exploration)
            const isError = (toolOutput.startsWith('Tool execution failed')
                         || toolOutput.startsWith('Invalid action'))
                         && !toolOutput.includes('Element not found')  // Normal during click exploration
                         && !toolOutput.includes('Relay')              // Relay retries are expected
                         && !toolOutput.includes('TIP:');              // Helpful error, not a real failure
            if (isError) {
                consecutiveErrors++;
            } else {
                consecutiveErrors = 0;
            }

            // Track summary stagnation
            const currentSummary = response.summary_of_findings || '';
            if (currentSummary === lastSummary || currentSummary.length < 5) {
                staleSummaryCount++;
            } else {
                staleSummaryCount = 0;
            }
            lastSummary = currentSummary;

            // Track post-checkpoint real work
            if (checkpointInjected) {
                postCheckpointActions++;
                const isRealWork = ['browse_web', 'run_command', 'execute_script', 'write_script'].includes(response.action);
                if (isRealWork && !isError) {
                    postCheckpointHasWork = true;
                }
            }

            // --- OpenClaw Context Pruning Implementation (V2 Hard Pruning) ---
            // Retain System prompt, User prompt, and the CURRENT logic chain. 
            // Aggressively prune HISTORIC Tool Results AND Assistant payload bodies to preserve token bandwidth while retaining reasoning.
            // --- OpenSpider V3 Token-Aware Context Pruning ---
            // Instead of blindly pruning every few turns (like OpenClaw), we dynamically monitor 
            // the actual memory payload length. If the commands are tiny, we retain 15+ turns of perfect clarity.
            // We only trigger skeletal compaction if the envelope gets dangerous (e.g. > 12,000 chars roughly 3.5k tokens).

            const totalLength = messages.reduce((acc, m) => acc + (typeof m.content === 'string' ? m.content.length : 0), 0);
            const DANGER_THRESHOLD = 15000; // Allow more context for browser-heavy tasks before pruning

            if (totalLength > DANGER_THRESHOLD) {
                console.log(`[Token Optimization] Context window dangerously large (${totalLength} chars). Triggering OpenSpider V3 Adaptive Pruning...`);

                // We keep the first 2 messages (system/initial user), and the VERY last turn. Everything in the middle is skeletonized to save bandwidth.
                for (let j = 2; j < messages.length - 2; j++) {
                    const msg = messages[j];

                    // 1. Prune User Tool Results
                    if (msg && msg.role === 'user' && typeof msg.content === 'string' && msg.content.startsWith('Tool Result:\n')) {
                        if (!msg.content.includes('[PRUNED_BY_OPENSPIDER]')) {
                            msg.content = `Tool Result:\n[PRUNED_BY_OPENSPIDER] Execution succeeded. See historic logs for raw stdout.`;
                        }
                    }

                    // 2. Prune Assistant JSON logic blocks (Thoughts and Source Code)
                    if (msg && msg.role === 'assistant' && typeof msg.content === 'string') {
                        if (!msg.content.includes('[PRUNED_BY_OPENSPIDER]')) {
                            try {
                                const payload = JSON.parse(msg.content);

                                // Preserve any explicit summary while dropping the massive realtime thought processing
                                const memory = payload.summary_of_findings || "No specific findings logged for this step.";
                                payload.thought = `[PRUNED_BY_OPENSPIDER] Kept logic in memory. Findings: ${memory}`;

                                // Strip raw code payloads if present to save massive tokens
                                if (payload.content) payload.content = "[PRUNED CODE STREAM]";
                                if (payload.command) payload.command = "[PRUNED COMMAND]";
                                if (payload.args) payload.args = "[PRUNED ARGS]";

                                msg.content = JSON.stringify(payload);
                            } catch (e) {
                                // If it's not valid JSON, we just let it pass
                            }
                        }
                    }
                }
            }

        }
        // Collect any summaries gathered across the loop and return them as a best-effort result
        const gatheredSummaries = messages
            .filter(m => m.role === 'user' && typeof m.content === 'string' && m.content.startsWith('[PRIOR AGENT ACTION HISTORY]'))
            .map(m => {
                try { return (JSON.parse((m.content as string).replace('[PRIOR AGENT ACTION HISTORY]: \n', '')))?.summary_of_findings; } catch { return null; }
            })
            .filter(Boolean)
            .join('\n');

        console.warn(`[Worker - ${this.role}] Hit budget limit (${currentBudget} steps, ${extensionsGranted} extensions). Returning best-effort summary.`);
        return gatheredSummaries
            ? `**Note: Task reached maximum step limit. Partial findings collected:**\n\n${gatheredSummaries}`
            : "Worker Agent hit max iteration limit without finding a final answer.";
    }
}

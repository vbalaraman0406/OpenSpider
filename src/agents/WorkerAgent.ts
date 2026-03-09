import { LLMProvider, ChatMessage } from '../llm/BaseProvider';
import { DynamicExecutor } from '../tools/DynamicExecutor';
import { BrowserTool, BrowseAction } from '../browser/tool';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { PersonaShell } from './PersonaShell';
import { sendWhatsAppMessage, sendWhatsAppAudio, getParticipatingGroups } from '../whatsapp';

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

    async executeTask(instruction: string, context: string[]): Promise<string> {
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
                    assignedSkillsContext = "\\n\\nYOUR ASSIGNED SKILLS:\\nYou have access to the following specialized tools. To use them, invoke `execute_script` with the listed filename.\\n";
                    const skillsDir = path.join(process.cwd(), 'skills');
                    for (const skill of workerProfile.skills) {
                        try {
                            const metadata = JSON.parse(fs.readFileSync(path.join(skillsDir, `${skill}.json`), 'utf-8'));
                            assignedSkillsContext += `\\n### Skill: ${skill}\\nFile: ${skill}.py\\nDescription: ${metadata.description}\\nInstructions: ${metadata.instructions}\\n`;
                        } catch (e) { }
                    }
                }
            }
        } catch (e) { console.error("Could not load worker profile."); }

        const persona = new PersonaShell(this.role);
        const compiledPersonaPrompt = persona.compileSystemPrompt();

        const systemPrompt = `${compiledPersonaPrompt}

[TASK INSTRUCTIONS]
Your Role: ${this.role}
You have the ability to write scripts (Python, Node.js, Bash) and execute them to solve the user's task.
If you need a package, write a script that installs it or ask to run npm install.
Your goal is to complete the task autonomously and return the final result.
CRITICAL TOKEN RULE: Do not print massive HTML dumps. Use Python to parse, summarize, and extract ONLY the exact data you need. Your tool output context is truncated to 3000 characters.
CRITICAL JSON TRUNCATION RULE: The backend API has a hard limit of 1500 output tokens. If your response exceeds this length, it will be forcefully clipped, causing a fatal JSON parse crash. You MUST keep your 'thought' string under 500 words and be concise in your intermediate steps to prevent array string truncation!
CRITICAL MACOS PRIVACY RULE: NEVER run commands to search, list, or read files in \`~/Desktop\`, \`~/Documents\`, or \`~/Downloads\` as this will trigger a strict macOS GUI permission dialog that blocks the backend. You must ONLY work within the current project directory \`${process.cwd()}\`.
CRITICAL COMPLETION RULE: You have a maximum of 40 steps. ALWAYS output final_answer as soon as you have enough information. For research tasks (finding businesses, data, lists), write final_answer after 3-5 sources — do NOT keep browsing trying to be exhaustive. Partial results delivered are ALWAYS better than a perfect answer never delivered. If a website fails to load after 2 attempts, move on immediately.
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
- send_voice: { "message": "Hello", "args": "voice_id" } (Send a voice note to the user via WhatsApp. The text in "message" will be converted to speech using ElevenLabs TTS and delivered as an audio message. Use "args" to optionally specify a voice ID.)
- update_whatsapp_whitelist: { "command": "add_dm", "target": "+14155552671" } (Safely grant or revoke WhatsApp access for users. "command" can be "add_dm", "remove_dm", "add_group", or "remove_group". "target" should be the raw phone number (e.g. +14155552671) or exact Group JID strings.)
- final_answer: { "result": "The final output" } (CRITICAL: You MUST include the 'result' key containing your answer)

BROWSER USAGE GUIDELINES:
- ALWAYS prefer browse_web over writing Python scripts for web searches, data lookup, or scraping. The browser is faster and uses fewer tokens.
- Typical flow: navigate → read_content → (optionally click/type if needed) → read_content → final_answer
- For Google searches: navigate to "https://www.google.com/search?q=your+query" then read_content.
- If a site requires login, use wait_for_user to ask the human to authenticate, then continue.

CRITICAL FORMATTING INSTRUCTION: 
When providing your \`final_answer\`, you MUST format the output to be highly readable and user-friendly. 
- ALWAYS use GitHub-flavored Markdown. 
- You MUST return the comprehensive, fully detailed list of your findings. DO NOT summarize or truncate the final result.
- If you are returning a list of items, data points, comparisons, or contractors, you MUST format it as a clean Markdown table with columns (e.g., Name, Website, Phone, Rating).
- Use bold text for emphasis and headers (##, ###) to separate sections logically.

Context from previous steps:
${context.join('\n')}
`;

        let messages: ChatMessage[] = [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: instruction }
        ];

        // Coding tasks (write→run→fix→repeat) need far more iterations than browsing tasks.
        // Detect coding-related roles and give them a much higher budget.
        const isCodingRole = /coder|developer|engineer|programmer|backend|frontend|fullstack|software|code/i.test(this.role);
        const maxLoops = isCodingRole ? 200 : 80;
        const warnAtIteration = isCodingRole ? 175 : 70; // Warn when ~25 steps remain

        // Autonomy Loop
        for (let i = 0; i < maxLoops; i++) {

            // Check for cancel at the top of every iteration
            if (this.cancelChecker && this.cancelChecker()) {
                console.log(`[Worker - ${this.role}] ⛔ Cancel detected at iteration ${i + 1}. Aborting task.`);
                return '⛔ Task cancelled by user.';
            }

            // --- Iteration budget warning ---
            // When approaching the limit, push a system message forcing the agent
            // to compile what it has gathered and issue a final_answer immediately.
            if (i === warnAtIteration) {
                console.warn(`[Worker - ${this.role}] ⚠️ Iteration budget warning at step ${i}/${maxLoops}. Forcing wrap-up.`);
                messages.push({
                    role: 'user',
                    content: `⚠️ SYSTEM: CRITICAL ITERATION BUDGET WARNING — You are on step ${i} of a maximum ${maxLoops}. You have approximately ${maxLoops - i} steps remaining before the task is forcibly terminated. You MUST wrap up NOW. Compile everything you have gathered into a final_answer IMMEDIATELY. Do NOT navigate to any more pages, do NOT run any more commands. Use your summary_of_findings to reconstruct the data and issue a final_answer with whatever results you have, even if incomplete. Partial results are INFINITELY better than no result.`
                });
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
                    toolOutput = await this.browserTool.execute(browseAction);
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
                            const cronPath = path.join(process.cwd(), 'workspace', 'cron_jobs.json');
                            let jobs: any[] = [];
                            if (fs.existsSync(cronPath)) {
                                jobs = JSON.parse(fs.readFileSync(cronPath, 'utf-8'));
                            }

                            // Upsert: check for existing job with the same name (case-insensitive)
                            const existingIndex = jobs.findIndex(
                                (j: any) => j.description.toLowerCase() === jobName.toLowerCase()
                            );

                            if (existingIndex !== -1) {
                                // UPDATE existing job in-place
                                const existing = jobs[existingIndex];
                                existing.prompt = taskPrompt;
                                existing.intervalHours = intervalHours;
                                if (preferredTime) {
                                    existing.preferredTime = preferredTime;
                                } else {
                                    delete existing.preferredTime; // Clear time-of-day if switching back to interval
                                }
                                fs.writeFileSync(cronPath, JSON.stringify(jobs, null, 2));
                                const scheduleStr = preferredTime ? `daily at ${preferredTime}` : `every ${intervalHours}h`;
                                console.log(`[Worker - ${this.role}] Updated existing cron job: "${jobName}" → ${scheduleStr}`);
                                toolOutput = `✅ Successfully updated existing cron job!\n- Name: ${jobName}\n- Schedule: ${scheduleStr}\n- New Task: ${taskPrompt.substring(0, 100)}...\n- Status: ${existing.status || 'enabled'}\n- ID: ${existing.id}`;
                            } else {
                                // CREATE new job (only if under the cap)
                                // SECURITY: Cap at 20 jobs max even from agent-scheduled tasks
                                if (jobs.length >= 20) {
                                    toolOutput = 'Error: Maximum of 20 cron jobs reached. Delete an existing job before scheduling a new one.';
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
                                    fs.writeFileSync(cronPath, JSON.stringify(jobs, null, 2));
                                    const scheduleStr = preferredTime ? `daily at ${preferredTime}` : `every ${intervalHours}h`;
                                    console.log(`[Worker - ${this.role}] Scheduled new recurring task: "${jobName}" ${scheduleStr}`);
                                    toolOutput = `✅ Successfully scheduled recurring task!\n- Name: ${jobName}\n- Schedule: ${scheduleStr}\n- Task: ${taskPrompt.substring(0, 100)}...\n- Status: Enabled\n- ID: ${newJob.id}`;
                                }
                            }
                        } catch (e: any) {
                            toolOutput = `Failed to schedule task: ${e.message}`;
                        }
                    }
                } else if (response.action === 'update_whatsapp_whitelist' && response.command && response.target) {
                    try {
                        const configPath = path.join(process.cwd(), 'workspace', 'whatsapp_config.json');
                        let waConfig: any = { dmPolicy: 'allowlist', allowedDMs: [], groupPolicy: 'allowlist', allowedGroups: [], botMode: 'mention' };
                        if (fs.existsSync(configPath)) {
                            waConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
                        }

                        const target = response.target.trim();
                        const rawNumber = target.replace(/\D/g, ''); // Extract just digits for DMs

                        if (response.command === 'add_dm' && rawNumber) {
                            if (!waConfig.allowedDMs) waConfig.allowedDMs = [];
                            const exists = waConfig.allowedDMs.some((e: any) =>
                                (typeof e === 'string' ? e : e.number || '').replace(/\D/g, '') === rawNumber
                            );
                            if (!exists) waConfig.allowedDMs.push({ number: rawNumber, mode: 'mention' });
                            toolOutput = `Successfully added ${rawNumber} to the WhatsApp Direct Messages Allowlist (mode: mention).`;
                        } else if (response.command === 'remove_dm' && rawNumber) {
                            if (waConfig.allowedDMs) {
                                waConfig.allowedDMs = waConfig.allowedDMs.filter((e: any) =>
                                    (typeof e === 'string' ? e : e.number || '').replace(/\D/g, '') !== rawNumber
                                );
                            }
                            toolOutput = `Successfully removed ${rawNumber} from the WhatsApp Direct Messages Allowlist.`;
                        } else if (response.command === 'add_group') {
                            if (!waConfig.allowedGroups) waConfig.allowedGroups = [];
                            const exists = waConfig.allowedGroups.some((g: any) => typeof g === 'string' ? g === target : g.jid === target);
                            if (!exists) waConfig.allowedGroups.push({ jid: target, mode: "mention" });
                            toolOutput = `Successfully added group ${target} to the Allowlist.`;
                        } else if (response.command === 'remove_group') {
                            if (waConfig.allowedGroups) {
                                waConfig.allowedGroups = waConfig.allowedGroups.filter((g: any) => typeof g === 'string' ? g !== target : g.jid !== target);
                            }
                            toolOutput = `Successfully removed group ${target} from the Allowlist.`;
                        } else {
                            toolOutput = `Error: Invalid command or target format.`;
                        }

                        fs.writeFileSync(configPath, JSON.stringify(waConfig, null, 2));
                        console.log(`[Worker - ${this.role}] Updated WhatsApp Allowlist via Agent Command.`);
                    } catch (e: any) {
                        toolOutput = `Failed to update WhatsApp whitelist: ${e.message}`;
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

            // [Token Optimization] Tighter output cap: browser page content is already
            // capped at 1,500 chars in tool.ts, so most outputs are small. For any
            // unexpected large output (e.g. script stdout), enforce a hard 1,500 char cap.
            const MAX_LENGTH = 1500;
            if (toolOutput.length > MAX_LENGTH) {
                const head = toolOutput.substring(0, 800);
                const tail = toolOutput.substring(toolOutput.length - 700);
                toolOutput = `${head}\n\n... [TRUNCATED ${toolOutput.length - MAX_LENGTH} characters. Write a script to parse/summarize if you need the full data] ...\n\n${tail}`;
            }

            console.log(`[Worker - ${this.role}] Tool Output: ${toolOutput.substring(0, 200)}...`);
            messages.push({ role: 'user', content: `Tool Result:\n${toolOutput}` });

            // --- OpenClaw Context Pruning Implementation (V2 Hard Pruning) ---
            // Retain System prompt, User prompt, and the CURRENT logic chain. 
            // Aggressively prune HISTORIC Tool Results AND Assistant payload bodies to preserve token bandwidth while retaining reasoning.
            // --- OpenSpider V3 Token-Aware Context Pruning ---
            // Instead of blindly pruning every few turns (like OpenClaw), we dynamically monitor 
            // the actual memory payload length. If the commands are tiny, we retain 15+ turns of perfect clarity.
            // We only trigger skeletal compaction if the envelope gets dangerous (e.g. > 12,000 chars roughly 3.5k tokens).

            const totalLength = messages.reduce((acc, m) => acc + (typeof m.content === 'string' ? m.content.length : 0), 0);
            const DANGER_THRESHOLD = 6000; // Lowered from 12000 — prune earlier to keep each LLM call under ~2k tokens

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

        console.warn(`[Worker - ${this.role}] Hit max iteration limit (${maxLoops}). Returning best-effort summary.`);
        return gatheredSummaries
            ? `**Note: Task reached maximum step limit. Partial findings collected:**\n\n${gatheredSummaries}`
            : "Worker Agent hit max iteration limit without finding a final answer.";
    }
}

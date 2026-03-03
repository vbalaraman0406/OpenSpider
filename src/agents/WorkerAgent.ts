import { LLMProvider, ChatMessage } from '../llm/BaseProvider';
import { DynamicExecutor } from '../tools/DynamicExecutor';
import { BrowserTool, BrowseAction } from '../browser/tool';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { PersonaShell } from './PersonaShell';
import { sendWhatsAppMessage, sendWhatsAppAudio } from '../whatsapp';

export class WorkerAgent {
    private llm: LLMProvider;
    private executor: DynamicExecutor;
    private browserTool: BrowserTool;
    private role: string;

    constructor(llm: LLMProvider, role: string) {
        this.llm = llm;
        this.executor = new DynamicExecutor();
        this.browserTool = new BrowserTool();
        this.role = role;
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
- schedule_task: { "command": "24", "content": "Fetch Vancouver WA weather and send to user via WhatsApp", "filename": "Daily Weather Brief" } (Schedule a recurring task that runs automatically. "command" = interval in hours, "content" = the prompt/task to execute, "filename" = short name for the job. The scheduler will auto-execute this task at the specified interval using the Manager Agent.)
- message_agent: { "target": "Role Name", "message": "Text to send" } (Delegate a sub-task to a specialized sub-agent)
- send_email: { "to": "user@example.com", "subject": "Hello", "body": "My message here" } (Send an outbound email natively using OAuth.)
- send_whatsapp: { "message": "Hello!" } (Send a WhatsApp message to the user. The system will automatically route to the configured user's WhatsApp number. Use this whenever the task requires sending results via WhatsApp.)
- send_voice: { "message": "Hello, how are you?", "args": "voice_id" } (Send a voice note to the user via WhatsApp. The text in "message" will be converted to speech using ElevenLabs TTS and delivered as an audio message. Use "args" to optionally specify a voice ID. Available voices:
  • "21m00Tcm4TlvDq8ikWAM" = Rachel (default, warm female)
  • "EXAVITQu4vr4xnSDxMaL" = Bella (soft female)
  • "ErXwobaYiN019PkySvjV" = Antoni (calm male)
  • "VR6AewLTigWG4xSOukaG" = Arnold (deep male)
  • "pNInz6obpgDQGcFmaJgB" = Adam (confident male)
  • "yoZ06aMxZJJ28mfd3POQ" = Sam (clear male)
  If the user asks for a specific voice style, pick the closest match. If no preference, omit "args" to use the default.)
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

        const maxLoops = 40; // Raised from 25 — research tasks need: navigate→read→click→read×N
        const warnAtIteration = 32; // Inject wrap-up warning when 8 iterations remain

        // Autonomy Loop
        for (let i = 0; i < maxLoops; i++) {

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
                    action: 'run_command' | 'write_script' | 'execute_script' | 'browse_web' | 'wait_for_user' | 'schedule_task' | 'message_agent' | 'send_email' | 'send_whatsapp' | 'send_voice' | 'final_answer';
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
                        action: { type: "string", enum: ["run_command", "write_script", "execute_script", "browse_web", "wait_for_user", "schedule_task", "message_agent", "send_email", "send_whatsapp", "send_voice", "final_answer"] },
                        thought: { type: "string" },
                        summary_of_findings: { type: "string", description: "A highly compressed, 1-2 sentence memory of what you learned in this step. Retained forever even if thoughts are pruned." },
                        command: { type: "string" },
                        filename: { type: "string" },
                        content: { type: "string" },
                        args: { type: "string" },
                        target: { type: "string" },
                        message: { type: "string" },
                        to: { type: "string" },
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
            console.log(`[Worker - ${this.role}] Thought: ${response.thought}`);
            console.log(`[Worker - RAW RESPONSE]`, JSON.stringify(response));

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
                    // command = sub-action (navigate/click/type/read_content/scroll/close)
                    // filename = URL (for navigate)
                    // args = CSS selector (for click/type) or direction (for scroll)
                    // content = text to type (for type)
                    const subAction = (response.command || 'navigate') as BrowseAction['action'];
                    const browseAction: BrowseAction = {
                        action: subAction,
                        url: response.filename,
                        selector: response.args,
                        text: response.content,
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
                    // command = interval in hours, content = the prompt, filename = job name
                    const intervalHours = parseFloat(response.command || '24');
                    const taskPrompt = response.content || response.message || '';
                    const jobName = response.filename || 'Scheduled Task';

                    if (!taskPrompt) {
                        toolOutput = 'Error: No task prompt provided for schedule_task. Provide the task description in the "content" field.';
                    } else {
                        try {
                            const cronPath = path.join(process.cwd(), 'workspace', 'cron_jobs.json');
                            let jobs: any[] = [];
                            if (fs.existsSync(cronPath)) {
                                jobs = JSON.parse(fs.readFileSync(cronPath, 'utf-8'));
                            }
                            const newJob = {
                                id: 'cron-' + Math.random().toString(36).substr(2, 9),
                                description: jobName,
                                prompt: taskPrompt,
                                intervalHours: intervalHours,
                                lastRunTimestamp: Date.now(), // Start counting from now, don't fire immediately
                                agentId: 'manager',
                                status: 'enabled'
                            };
                            jobs.push(newJob);
                            fs.writeFileSync(cronPath, JSON.stringify(jobs, null, 2));
                            console.log(`[Worker - ${this.role}] Scheduled recurring task: "${jobName}" every ${intervalHours}h`);
                            toolOutput = `✅ Successfully scheduled recurring task!\n- Name: ${jobName}\n- Interval: Every ${intervalHours} hours\n- Task: ${taskPrompt}\n- Status: Enabled\n- ID: ${newJob.id}\n\nThe scheduler heartbeat checks every 60 seconds and will auto-execute this task at the specified interval.`;
                        } catch (e: any) {
                            toolOutput = `Failed to schedule task: ${e.message}`;
                        }
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
                } else if (response.action === 'send_whatsapp' && response.message) {
                    console.log(`[Worker - ${this.role}] Sending WhatsApp message...`);
                    try {
                        // Determine the user's WhatsApp JID from the config
                        const configPath = path.join(process.cwd(), 'workspace', 'whatsapp_config.json');
                        let userJid = '';
                        if (fs.existsSync(configPath)) {
                            const waConfig = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
                            if (waConfig.allowedDMs && waConfig.allowedDMs.length > 0) {
                                const rawNumber = waConfig.allowedDMs[0].replace(/\D/g, '');
                                userJid = `${rawNumber}@s.whatsapp.net`;
                            }
                        }
                        if (!userJid) {
                            toolOutput = 'Error: No WhatsApp user configured. Add a phone number to the allowedDMs list in Channels > WhatsApp config.';
                        } else {
                            // Get agent persona name for the header
                            let agentName = 'OpenSpider';
                            try {
                                const persona = new PersonaShell('manager');
                                const caps = persona.getCapabilities();
                                if (caps && caps.name) agentName = caps.name;
                            } catch (e) { }

                            const formattedMsg = `✨ *${agentName}*\n\n${response.message}`;
                            await sendWhatsAppMessage(userJid, formattedMsg);
                            toolOutput = `✅ WhatsApp message sent successfully to ${userJid}.`;
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
                                const rawNumber = waConfig.allowedDMs[0].replace(/\D/g, '');
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

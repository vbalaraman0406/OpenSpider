import { LLMProvider, ChatMessage } from '../llm/BaseProvider';
import { DynamicExecutor } from '../tools/DynamicExecutor';
import fs from 'node:fs';
import path from 'node:path';
import { PersonaShell } from './PersonaShell';

export class WorkerAgent {
    private llm: LLMProvider;
    private executor: DynamicExecutor;
    private role: string;

    constructor(llm: LLMProvider, role: string) {
        this.llm = llm;
        this.executor = new DynamicExecutor();
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
${assignedSkillsContext}

Available tools you can request in your JSON response:
- run_command: { "command": "echo hello" } (Run a bash command within the project environment)
- write_script: { "filename": "test.py", "content": "print('hello')" } (Write a code script to disk)
- execute_script: { "filename": "test.py", "args": "" } (Execute a dynamically written script)
- message_agent: { "target": "Role Name", "message": "Text to send" } (Delegate a sub-task to a specialized sub-agent)
- send_email: { "to": "user@example.com", "subject": "Hello", "body": "My message here" } (Send an outbound email natively using OAuth. Use this automatically if asked to email someone.)
- final_answer: { "result": "The final output" } (CRITICAL: You MUST include the 'result' key containing your answer)

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

        const maxLoops = 25;

        // Autonomy Loop
        for (let i = 0; i < maxLoops; i++) {


            let response;
            try {
                response = await this.llm.generateStructuredOutputs<{
                    action: 'run_command' | 'write_script' | 'execute_script' | 'message_agent' | 'send_email' | 'final_answer';
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
                        action: { type: "string", enum: ["run_command", "write_script", "execute_script", "message_agent", "send_email", "final_answer"] },
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
                } else if (response.action === 'send_email' && response.to && response.subject && response.body) {
                    console.log(`[Worker - ${this.role}] Dispatching email to ${response.to}...`);
                    try {
                        const path = require('node:path');
                        const { execSync } = require('node:child_process');
                        const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..', '..') : path.join(__dirname, '..', '..');
                        const pythonScript = path.join(rootDir, 'skills', 'send_email.py');

                        // We safely escape quotes to prevent injection into the python args
                        const safeTo = response.to.replace(/"/g, '\\"');
                        const safeSubject = response.subject.replace(/"/g, '\\"');
                        const safeBody = response.body.replace(/"/g, '\\"');

                        const stdout = execSync(`python3 "${pythonScript}" --to "${safeTo}" --subject "${safeSubject}" --body "${safeBody}"`);
                        toolOutput = `Email sent successfully:\n${stdout.toString()}`;
                    } catch (e: any) {
                        toolOutput = `Failed to send email. Ensure OAuth is configured via 'openspider tools email setup'. Error: ${e.message}\n${e.stdout?.toString() || ''}\n${e.stderr?.toString() || ''}`;
                    }
                } else {
                    toolOutput = `Invalid action or missing parameters. You requested '${response.action}'. Check the schema. run_command needs 'command', write_script needs 'filename' and 'content', send_email needs 'to', 'subject', and 'body'. You provided: ${JSON.stringify(response)}`;
                }
            } catch (e: any) {
                toolOutput = `Tool execution failed: ${e.message}`;
            }

            // [V3] High Token Usage Fix: Smart Head & Tail Truncation for massive scraping outputs
            const MAX_LENGTH = 3000;
            if (toolOutput.length > MAX_LENGTH) {
                const head = toolOutput.substring(0, 1500);
                const tail = toolOutput.substring(toolOutput.length - 1500);
                toolOutput = `${head}\n\n... [TRUNCATED ${toolOutput.length - 3000} characters. You must write scripts to parse/summarize if you need the middle data] ...\n\n${tail}`;
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
            const DANGER_THRESHOLD = 12000;

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
        return "Worker Agent hit max iteration limit without finding a final answer.";
    }
}

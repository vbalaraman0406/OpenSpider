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
${assignedSkillsContext}

Available tools you can request in your JSON response:
- run_command: { "command": "echo hello" }
- write_script: { "filename": "test.py", "content": "print('hello')" }
- execute_script: { "filename": "test.py", "args": "" }
- message_agent: { "target": "Role Name", "message": "Text to send" }
- final_answer: { "result": "The final output" }

Context from previous steps:
${context.join('\n')}
`;

        let messages: ChatMessage[] = [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: instruction }
        ];

        const maxLoops = 10;

        // Autonomy Loop
        for (let i = 0; i < maxLoops; i++) {
            // Inject human-like IDE typing delay to prevent bot/velocity detection ONLY for internal IDE
            if (this.llm.providerName === 'antigravity-internal') {
                const delayMs = Math.floor(Math.random() * (8000 - 3000 + 1)) + 3000;
                console.log(`[Worker - ${this.role}] Emulating human typing delay (${Math.round(delayMs / 1000)}s)...`);
                await new Promise(r => setTimeout(r, delayMs));
            }

            const response = await this.llm.generateStructuredOutputs<{
                action: 'run_command' | 'write_script' | 'execute_script' | 'message_agent' | 'final_answer';
                command?: string;
                filename?: string;
                content?: string;
                args?: string;
                target?: string;
                message?: string;
                result?: string;
                thought: string;
            }>(messages, {
                type: "object",
                properties: {
                    action: { type: "string", enum: ["run_command", "write_script", "execute_script", "message_agent", "final_answer"] },
                    thought: { type: "string" },
                    command: { type: "string" },
                    filename: { type: "string" },
                    content: { type: "string" },
                    args: { type: "string" },
                    target: { type: "string" },
                    message: { type: "string" },
                    result: { type: "string" }
                },
                required: ["action", "thought"]
            });

            // Log the thought process (useful for the DB / Dashboard later)
            console.log(`[Worker - ${this.role}] Thought: ${response.thought}`);
            console.log(`[Worker - RAW RESPONSE]`, JSON.stringify(response));
            messages.push({ role: 'assistant', content: JSON.stringify(response) });

            if (response.action === 'final_answer') {
                return response.result || "Task completed without explicit result.";
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
                } else {
                    toolOutput = `Invalid action or missing parameters. You requested '${response.action}'. Check the schema. run_command needs 'command', write_script needs 'filename' and 'content', execute_script needs 'filename', message_agent needs 'target' and 'message'. You provided: ${JSON.stringify(response)}`;
                }
            } catch (e: any) {
                toolOutput = `Tool execution failed: ${e.message}`;
            }

            console.log(`[Worker - ${this.role}] Tool Output: ${toolOutput.substring(0, 200)}...`);
            messages.push({ role: 'user', content: `Tool Result:\n${toolOutput}` });
        }

        return "Worker Agent hit max iteration limit without finding a final answer.";
    }
}

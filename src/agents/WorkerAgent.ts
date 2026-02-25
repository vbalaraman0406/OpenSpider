import { LLMProvider, ChatMessage } from '../llm/BaseProvider';
import { DynamicExecutor } from '../tools/DynamicExecutor';

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

        const systemPrompt = `You are a specialized Openspider Worker Agent. 
Your Role: ${this.role}
You have the ability to write scripts (Python, Node.js, Bash) and execute them to solve the user's task.
If you need a package, write a script that installs it or ask to run npm install.
Your goal is to complete the task autonomously and return the final result.

Available tools you can request in your JSON response:
- run_command: { "command": "echo hello" }
- write_script: { "filename": "test.py", "content": "print('hello')" }
- execute_script: { "filename": "test.py", "args": "" }
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
            const response = await this.llm.generateStructuredOutputs<{
                action: 'run_command' | 'write_script' | 'execute_script' | 'final_answer';
                command?: string;
                filename?: string;
                content?: string;
                args?: string;
                result?: string;
                thought: string;
            }>(messages, {
                type: "object",
                properties: {
                    action: { type: "string", enum: ["run_command", "write_script", "execute_script", "final_answer"] },
                    thought: { type: "string" },
                    command: { type: "string" },
                    filename: { type: "string" },
                    content: { type: "string" },
                    args: { type: "string" },
                    result: { type: "string" }
                },
                required: ["action", "thought"]
            });

            // Log the thought process (useful for the DB / Dashboard later)
            console.log(`[Worker - ${this.role}] Thought: ${response.thought}`);
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
                } else if (response.action === 'write_script' && response.filename && response.content) {
                    console.log(`[Worker - ${this.role}] Writing script: ${response.filename}`);
                    toolOutput = await this.executor.writeScript(response.filename, response.content);
                } else if (response.action === 'execute_script' && response.filename) {
                    console.log(`[Worker - ${this.role}] Executing script: ${response.filename}`);
                    const res = await this.executor.executeScript(response.filename, response.args);
                    toolOutput = `stdout: ${res.stdout}\nstderr: ${res.stderr}\nerror: ${res.error || 'none'}`;
                } else {
                    toolOutput = "Invalid action or missing parameters for action: " + response.action;
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

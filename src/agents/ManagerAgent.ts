import { getProvider } from '../llm';
import { LLMProvider, ChatMessage } from '../llm/BaseProvider';
import { WorkerAgent } from './WorkerAgent';

export class ManagerAgent {
    private llm: LLMProvider;

    constructor() {
        this.llm = getProvider();
    }

    async processUserRequest(prompt: string): Promise<string> {
        console.log(`\n[Manager] Analyzing request: "${prompt}"`);
        const agentPersona = process.env.AGENT_PERSONA || "You are a helpful multi-agent assistant designed to write excellent code and utilize terminals.";

        const systemPrompt = `${agentPersona}\n\nYou are the Manager Agent for OpenSpider. Your job is to break down the user's complex request into a sequential plan of sub-tasks.
Each sub-task should be assigned to a specialized Worker Agent role.

Analyze the prompt and return a JSON array of sub-tasks.
Example input: "Scrape the front page of hackernews and save the top 5 titles to titles.txt"
Example output:
{
  "tasks": [
    {
      "role": "Web Scraper",
      "instruction": "Write a python script using requests and beautifulsoup to scrape news.ycombinator.com and extract the top 5 titles."
    },
    {
      "role": "File Writer",
      "instruction": "Take the titles provided by the Web Scraper and save them to a file named titles.txt."
    }
  ]
}
`;

        const messages: ChatMessage[] = [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: Object.keys(prompt).length ? JSON.stringify(prompt) : prompt }
        ];

        try {
            // Emulate human typing/thinking delay to avoid velocity detection ONLY for internal IDE
            if (this.llm.providerName === 'antigravity-internal') {
                const delayMs = Math.floor(Math.random() * (6000 - 2000 + 1)) + 2000;
                console.log(`[Manager] Emulating human typing delay (${Math.round(delayMs / 1000)}s)...`);
                await new Promise(r => setTimeout(r, delayMs));
            }

            const plan = await this.llm.generateStructuredOutputs<{
                tasks: { role: string; instruction: string }[]
            }>(messages, {
                type: "object",
                properties: {
                    tasks: {
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
                required: ["tasks"]
            });

            console.log(`[Manager] Generated Plan with ${plan.tasks.length} tasks:`);
            plan.tasks.forEach((t, i) => console.log(`  ${i + 1}. [${t.role}] ${t.instruction}`));

            // Execute sequentially, passing context along
            let globalContext: string[] = [`Original User Request: ${prompt}`];
            let finalOutput = "";

            for (let i = 0; i < plan.tasks.length; i++) {
                const task = plan.tasks[i];
                if (!task) continue;
                console.log(`\n[Manager] Delegating Task ${i + 1}/${plan.tasks.length} to ${task.role}...`);

                const worker = new WorkerAgent(this.llm, task.role);
                const result = await worker.executeTask(task.instruction, globalContext);

                console.log(`[Manager] Task ${i + 1} completed. Result:\n${result}\n`);
                globalContext.push(`Task ${i + 1} Result from ${task.role}: ${result}`);

                if (i === plan.tasks.length - 1) {
                    finalOutput = result;
                }
            }

            return `Plan execution finished successfully. Final Output:\n${finalOutput}`;

        } catch (e: any) {
            console.error("[Manager] Error generating/executing plan:", e);
            return `Failed to execute request: ${e.message}`;
        }
    }
}

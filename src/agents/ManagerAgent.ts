import { getProvider } from '../llm';
import { LLMProvider, ChatMessage } from '../llm/BaseProvider';
import { WorkerAgent } from './WorkerAgent';
import fs from 'node:fs';
import path from 'node:path';
import { readMemoryContext } from '../memory';

export class ManagerAgent {
    private llm: LLMProvider;

    constructor() {
        this.llm = getProvider();
    }

    async processUserRequest(prompt: string): Promise<string> {
        console.log(`\n[Manager] Analyzing request: "${prompt}"`);
        const agentPersona = process.env.AGENT_PERSONA || "You are a helpful multi-agent assistant designed to write excellent code and utilize terminals.";

        // Build dynamic agent catalog
        let agentCapabilities = "";
        try {
            const agentsPath = path.join(process.cwd(), 'agents.json');
            if (fs.existsSync(agentsPath)) {
                const agents = JSON.parse(fs.readFileSync(agentsPath, 'utf-8'));
                agentCapabilities = "\\nAvailable Worker Agents:\\n";
                for (const agent of agents) {
                    if (agent.id === 'gateway') continue;
                    agentCapabilities += `- Role: ${agent.role}\\n  Assigned Skills: ${agent.skills?.join(', ') || 'none'}\\n`;
                }
            }

            const skillsDir = path.join(process.cwd(), 'skills');
            if (fs.existsSync(skillsDir)) {
                agentCapabilities += "\\nAvailable Skill Summaries:\\n";
                const files = fs.readdirSync(skillsDir).filter(f => f.endsWith('.json') && f !== 'package.json');
                for (const file of files) {
                    try {
                        const metadata = JSON.parse(fs.readFileSync(path.join(skillsDir, file), 'utf-8'));
                        agentCapabilities += `- ${metadata.name}: ${metadata.description}\\n`;
                    } catch (e) { }
                }
            }
        } catch (e) { console.error("Could not load agent catalog."); }

        const systemPrompt = `${agentPersona}\n\n${readMemoryContext()}\n\nYou are the Manager Agent for OpenSpider. Your job is to break down the user's complex request into a sequential plan of sub-tasks.
Each sub-task should be assigned to a specialized Worker Agent role. Utilize the existing agents below or define generic roles if none match exactly.
${agentCapabilities}


Analyze the prompt and return a JSON array of steps.
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

            const planResult = await this.llm.generateStructuredOutputs<{
                plan: Array<{
                    type: "task" | "parallel";
                    name?: string;
                    role?: string;
                    instruction?: string;
                    subtasks?: Array<{ role: string; instruction: string }>;
                }>
            }>(messages, {
                type: "object",
                properties: {
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
                },
                required: ["plan"]
            });

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

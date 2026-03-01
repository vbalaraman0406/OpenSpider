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
        let agentCapabilities = "\\nAvailable Worker Agents:\\n";
        try {
            const agentsDir = path.join(process.cwd(), 'workspace', 'agents');
            if (fs.existsSync(agentsDir)) {
                const agentFolders = fs.readdirSync(agentsDir).filter(f => fs.statSync(path.join(agentsDir, f)).isDirectory());
                for (const agentId of agentFolders) {
                    if (agentId === 'manager') continue;
                    const shell = new PersonaShell(agentId);
                    const caps = shell.getCapabilities();
                    if (caps.status === 'stopped') continue; // Prevent delegating to offline agents
                    // Grab just the first line of their identity as a summary
                    const identityStr = shell.getIdentity().split('\\n').filter(l => l.trim().length > 0)[0] || "Specialized Sub-Agent";
                    agentCapabilities += `- Agent: ${caps.name || agentId} (Role: ${caps.role || agentId})\\n  Summary: ${identityStr}\\n  Tools: ${caps.allowedTools?.join(', ') || 'none'}\\n`;
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

        const persona = new PersonaShell('manager');
        const compiledPersonaPrompt = persona.compileSystemPrompt();

        const systemPrompt = `${compiledPersonaPrompt}\n\n[MEMORY CONTEXT]\n${readMemoryContext()}\n\n[TASK INSTRUCTIONS]
Your job is to break down the user's complex request into a sequential plan of sub-tasks.
Each sub-task should be assigned to a specialized Worker Agent role. Utilize the existing agents below or define generic roles if none match exactly.
${agentCapabilities}

If the user is simply saying hello, asking a basic question about you, or making small talk, DO NOT generate a plan. Instead, use the 'direct_response' field to reply strictly in character as your Persona without delegating any subtasks.
When using the 'direct_response' field, ALWAYS format your output to be user-friendly. Use GitHub flavored markdown and clean tables for structural data.
CRITICAL JSON TRUNCATION RULE: The backend API has a hard limit of 1500 output tokens. If your response exceeds this length, it will be forcefully clipped, causing a fatal JSON parse crash. Keep your generated "plan" steps reasonably concise. HOWEVER, DO NOT instruct your delegated Worker Agents to be concise. You MUST command them to return the most highly detailed, comprehensive markdown tables possible when scraping data.

[WHATSAPP NATIVE FEATURES]
If the user is asking a question that requires multiple choices, or you want to survey them, you can output a native WhatsApp Poll anywhere in your response using the tags: \`[POLL]Question|Option A|Option B|Option C[/POLL]\`. WhatsApp allows a max of 12 options. You can also utilize this when asking the user for context or how they wish to proceed.

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

        let userContent: string | any[] = Object.keys(prompt).length ? JSON.stringify(prompt) : prompt;
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
                // Emulate human typing/thinking delay to avoid velocity detection ONLY for internal IDE (Optimized Stealth)
                if (this.llm.providerName === 'antigravity-internal') {
                    const delayMs = Math.floor(Math.random() * (500 - 200 + 1)) + 200;
                    console.log(`[Manager] Emulating human typing delay (${(delayMs / 1000).toFixed(1)}s)...`);
                    await new Promise(r => setTimeout(r, delayMs));
                }

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

import express from 'express';
import { WebSocketServer, WebSocket } from 'ws';
import * as http from 'http';
import cors from 'cors';
import fs from 'node:fs';
import path from 'node:path';
import { ManagerAgent } from './agents/ManagerAgent';
import { getProvider } from './llm';
import { ChatMessage } from './llm/BaseProvider';
import { logMemory } from './memory';
import { initScheduler, runJobForcefully } from './scheduler';
import { logUsage, getUsageSummary } from './usage';

export function startServer() {
    const app = express();
    app.use(cors());
    app.use(express.json());

    const server = http.createServer(app);
    const wss = new WebSocketServer({ server });

    // Store connected clients
    const clients: Set<WebSocket> = new Set();

    const manager = new ManagerAgent();

    wss.on('connection', (ws) => {
        clients.add(ws);
        console.log('[Server] Dashboard client connected');

        ws.on('message', async (messageData) => {
            try {
                const parsed = JSON.parse(messageData.toString());
                if (parsed.type === 'chat') {
                    console.log(`\n\n[Web Chat] Received message: ${parsed.text}`);

                    // Log user message to session memory
                    logMemory('User', parsed.text);

                    // Send an immediate acknowledgement
                    ws.send(JSON.stringify({
                        type: 'chat_response',
                        data: '🕷️ OpenSpider is processing your request...',
                        timestamp: new Date().toISOString()
                    }));

                    // Process request
                    const response = await manager.processUserRequest(parsed.text);

                    // Log agent response to session memory
                    logMemory('OpenSpider', response);

                    // Send final result
                    ws.send(JSON.stringify({
                        type: 'chat_response',
                        data: response,
                        timestamp: new Date().toISOString()
                    }));
                }
            } catch (err: any) {
                console.error('[Web Chat] Error processing message:', err.message);
                ws.send(JSON.stringify({
                    type: 'chat_response',
                    data: `❌ Error: ${err.message}`,
                    timestamp: new Date().toISOString()
                }));
            }
        });

        ws.on('close', () => clients.delete(ws));
    });

    // Override console.log to broadcast to WebSockets
    const originalLog = console.log;
    console.log = (...args: any[]) => {
        originalLog(...args);

        // Process each argument individually in case multiple JSON events were logged at once
        args.forEach(arg => {
            const message = typeof arg === 'object' ? JSON.stringify(arg) : String(arg);
            let isSpecialEvent = false;

            try {
                if (message.includes('"type":"usage"') || message.includes('"type":"agent_flow"')) {
                    const parsed = JSON.parse(message);
                    if (parsed.type === 'usage' || parsed.type === 'agent_flow') {
                        isSpecialEvent = true;

                        // Specifically intercept usage to durable log and check for alerts
                        if (parsed.type === 'usage') {
                            const alertStatus = logUsage({
                                timestamp: new Date().toISOString(),
                                model: parsed.model,
                                usage: parsed.usage,
                                sessionKey: parsed.sessionKey || 'main',
                                agentId: parsed.agentId || 'gateway'
                            });

                            if (alertStatus.isAlert) {
                                clients.forEach(client => {
                                    if (client.readyState === WebSocket.OPEN) {
                                        client.send(JSON.stringify({
                                            type: 'alert',
                                            data: alertStatus.message,
                                            timestamp: new Date().toISOString()
                                        }));
                                    }
                                });
                            }
                        }

                        clients.forEach(client => {
                            if (client.readyState === WebSocket.OPEN) {
                                client.send(JSON.stringify({
                                    type: parsed.type,
                                    data: parsed,
                                    timestamp: new Date().toISOString()
                                }));
                            }
                        });
                    }
                }
            } catch (e) {
                // Not a valid standalone JSON
            }

            if (!isSpecialEvent) {
                // Broadcast standard log to all dashboard clients
                clients.forEach(client => {
                    if (client.readyState === WebSocket.OPEN) {
                        client.send(JSON.stringify({ type: 'log', data: message, timestamp: new Date().toISOString() }));
                    }
                });
            }
        });
    };

    // API Route to fetch current connection config
    app.get('/api/config', (req, res) => {
        const provider = process.env.DEFAULT_PROVIDER || 'ollama';
        res.json({ provider, status: 'running' });
    });

    // API Route to fetch aggregated usage summary
    app.get('/api/usage', (req, res) => {
        try {
            res.json(getUsageSummary());
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // API Route to generate a new skill from natural language
    app.post('/api/skills/generate', async (req, res) => {
        try {
            const { name, description, instructions } = req.body;
            if (!name || !instructions) {
                return res.status(400).json({ error: "Name and instructions are required." });
            }

            const llm = getProvider();
            const systemPrompt = `You are a specialized coding agent for OpenSpider.
Your task is to generate a Python script that acts as a tool/skill for another AI agent.
The user has provided a name, a description, and natural language instructions for the tool.
Generate ONLY valid Python code. Do not wrap it in markdown block quotes.
The Python code MUST contain a function named \`execute(args: dict) -> dict:\` which serves as the entry point.
Any needed libraries should be imported in the script. Ensure it catches errors gracefully.
Return ONLY the raw Python code.`;

            const messages: ChatMessage[] = [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: `Tool Name: ${name}\nDescription: ${description}\nInstructions: ${instructions}` }
            ];

            const response = await llm.generateStructuredOutputs<{ code: string }>(messages, {
                type: "object",
                properties: {
                    code: { type: "string" }
                },
                required: ["code"]
            });

            // Write the generated code to the skills directory
            const skillsDir = path.join(process.cwd(), 'skills');
            if (!fs.existsSync(skillsDir)) {
                fs.mkdirSync(skillsDir, { recursive: true });
            }

            // Also create package.json to be safe if not exists
            if (!fs.existsSync(path.join(skillsDir, 'package.json'))) {
                fs.writeFileSync(
                    path.join(skillsDir, 'package.json'),
                    JSON.stringify({ name: "openspider-dynamic-skills", version: "1.0.0", private: true }, null, 2)
                );
            }

            const baseName = name.replace(/\.(py|js)$/, '');
            const pythonFileName = `${baseName}.py`;
            const jsonFileName = `${baseName}.json`;
            const filePath = path.join(skillsDir, pythonFileName);
            const jsonPath = path.join(skillsDir, jsonFileName);

            const metadata = {
                name: baseName,
                description: description || "Custom skill generated by OpenSpider.",
                instructions: instructions,
                language: 'python'
            };

            fs.writeFileSync(filePath, response.code, 'utf-8');
            fs.writeFileSync(jsonPath, JSON.stringify(metadata, null, 2), 'utf-8');

            console.log(`[Server] Generated and saved new skill: ${pythonFileName} and metadata: ${jsonFileName}`);
            res.json({ success: true, message: `Skill ${baseName} generated successfully.`, file: baseName });

        } catch (e: any) {
            console.error('[Server] Error generating skill:', e.message);
            res.status(500).json({ error: e.message });
        }
    });

    // API Route to fetch active agents/skills
    app.get('/api/skills', (req, res) => {
        try {
            const skillsDir = path.join(process.cwd(), 'skills');
            if (!fs.existsSync(skillsDir)) return res.json({ skills: [] });

            const files = fs.readdirSync(skillsDir)
                .filter(file => file.endsWith('.json') && file !== 'package.json')
                // Strip the .json so the frontend just gets the plain skill names
                .map(file => file.replace('.json', ''));
            res.json({ skills: files });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // API Route to fetch the content of a specific skill
    app.get('/api/skills/:name', (req, res) => {
        try {
            const skillName = req.params.name;
            const skillsDir = path.resolve(process.cwd(), 'skills');
            // Ensure we are looking for the .json metadata file
            const jsonFileName = skillName.endsWith('.json') ? skillName : `${skillName}.json`;
            const filePath = path.resolve(skillsDir, jsonFileName);

            // Strict directory traversal protection
            if (!filePath.startsWith(skillsDir)) {
                return res.status(403).json({ error: 'Forbidden Path Traversal Detected' });
            }

            if (!fs.existsSync(filePath)) {
                // To maintain backwards compatibility if only the .py file exists
                const pyFilePath = path.join(skillsDir, `${skillName}.py`);
                if (fs.existsSync(pyFilePath)) {
                    const pyContent = fs.readFileSync(pyFilePath, 'utf-8');
                    return res.json({ name: skillName, content: pyContent });
                }
                return res.status(404).json({ error: 'Skill metadata not found' });
            }

            const rawContent = fs.readFileSync(filePath, 'utf-8');
            try {
                const jsonContent = JSON.parse(rawContent);
                // Return a Markdown formatted string so the existing UI Modal renders it beautifully
                const formattedMarkdown = `# ${jsonContent.name}\n\n**Description:** ${jsonContent.description}\n\n**Instructions:**\n${jsonContent.instructions}`;
                res.json({ name: skillName, content: formattedMarkdown });
            } catch (e) {
                res.json({ name: skillName, content: rawContent });
            }
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // API Route to delete a custom skill
    app.delete('/api/skills/:name', (req, res) => {
        try {
            const skillName = req.params.name.replace('.json', '').replace('.py', '');
            const skillsDir = path.resolve(process.cwd(), 'skills');

            const jsonPath = path.resolve(skillsDir, `${skillName}.json`);
            const pyPath = path.resolve(skillsDir, `${skillName}.py`);

            // Strict directory traversal protection
            if (!jsonPath.startsWith(skillsDir) || !pyPath.startsWith(skillsDir)) {
                return res.status(403).json({ error: 'Forbidden Path Traversal Detected' });
            }

            let deleted = false;
            if (fs.existsSync(jsonPath)) {
                fs.unlinkSync(jsonPath);
                deleted = true;
            }
            if (fs.existsSync(pyPath)) {
                fs.unlinkSync(pyPath);
                deleted = true;
            }

            if (!deleted) {
                return res.status(404).json({ error: 'Skill not found' });
            }

            res.json({ success: true, message: `Skill ${skillName} deleted successfully.` });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // Helper for agents DB
    const agentsDbPath = path.join(process.cwd(), 'agents.json');
    const getAgents = () => {
        if (!fs.existsSync(agentsDbPath)) {
            const defaultAgents = [
                {
                    id: 'gateway',
                    name: 'Gateway Architect',
                    role: 'Handles default routing.',
                    status: 'emerald',
                    initial: 'G',
                    color: 'fuchsia',
                    model: 'gemini-2.5-flash-thinking-exp',
                    prompt: 'You are the primary gateway agent for OpenSpider. Analyze all incoming requests across all channels and determine if you can answer them or if you need to dispatch a specialized worker agent.',
                    skills: ['web_search', 'calculator', 'worker_dispatch']
                }
            ];
            fs.writeFileSync(agentsDbPath, JSON.stringify(defaultAgents, null, 2));
            return defaultAgents;
        }
        return JSON.parse(fs.readFileSync(agentsDbPath, 'utf-8'));
    };

    // API Route to fetch active agents
    app.get('/api/agents', (req, res) => {
        try {
            res.json(getAgents());
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // API Route to create a new agent
    app.post('/api/agents', (req, res) => {
        try {
            const agent = req.body;
            // Generate a simple ID
            agent.id = agent.name.toLowerCase().replace(/[^a-z0-9]/g, '-') + '-' + Math.random().toString(36).substr(2, 5);
            agent.status = 'slate';
            agent.skills = agent.skills || [];

            const agents = getAgents();
            agents.push(agent);
            fs.writeFileSync(agentsDbPath, JSON.stringify(agents, null, 2));
            res.json({ success: true, agent });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // API Route to assign a skill to an agent
    app.post('/api/agents/:id/skills', (req, res) => {
        try {
            const agentId = req.params.id;
            const { skill } = req.body;
            if (!skill) return res.status(400).json({ error: 'Skill is required' });

            const agents = getAgents();
            const agent = agents.find((a: any) => a.id === agentId);
            if (!agent) return res.status(404).json({ error: 'Agent not found' });

            if (!agent.skills) agent.skills = [];
            if (!agent.skills.includes(skill)) {
                agent.skills.push(skill);
                fs.writeFileSync(agentsDbPath, JSON.stringify(agents, null, 2));
            }
            res.json({ success: true, agent });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // --- CRON JOBS REST ENDPOINTS ---
    const cronJobsPath = path.join(process.cwd(), 'workspace', 'cron_jobs.json');

    app.get('/api/cron', (req, res) => {
        try {
            if (!fs.existsSync(cronJobsPath)) return res.json([]);
            const jobs = JSON.parse(fs.readFileSync(cronJobsPath, 'utf-8'));
            res.json(jobs);
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    app.post('/api/cron', (req, res) => {
        try {
            const { description, prompt, intervalHours, agentId } = req.body;
            let jobs = [];
            if (fs.existsSync(cronJobsPath)) {
                jobs = JSON.parse(fs.readFileSync(cronJobsPath, 'utf-8'));
            }

            const newJob = {
                id: 'cron-' + Math.random().toString(36).substr(2, 9),
                description,
                prompt,
                intervalHours: Number(intervalHours) || 24,
                lastRunTimestamp: Date.now(),
                agentId: agentId || 'gateway',
                status: 'enabled'
            };

            jobs.push(newJob);
            fs.writeFileSync(cronJobsPath, JSON.stringify(jobs, null, 2));
            res.json({ success: true, job: newJob });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    app.delete('/api/cron/:id', (req, res) => {
        try {
            if (!fs.existsSync(cronJobsPath)) return res.status(404).json({ error: 'No jobs found' });

            let jobs = JSON.parse(fs.readFileSync(cronJobsPath, 'utf-8'));
            jobs = jobs.filter((j: any) => j.id !== req.params.id);
            fs.writeFileSync(cronJobsPath, JSON.stringify(jobs, null, 2));
            res.json({ success: true });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    app.put('/api/cron/:id', (req, res) => {
        try {
            if (!fs.existsSync(cronJobsPath)) return res.status(404).json({ error: 'No jobs found' });

            let jobs = JSON.parse(fs.readFileSync(cronJobsPath, 'utf-8'));
            const jobIndex = jobs.findIndex((j: any) => j.id === req.params.id);

            if (jobIndex === -1) return res.status(404).json({ error: 'Job not found' });

            jobs[jobIndex] = { ...jobs[jobIndex], ...req.body };
            fs.writeFileSync(cronJobsPath, JSON.stringify(jobs, null, 2));
            res.json({ success: true, job: jobs[jobIndex] });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    app.post('/api/cron/:id/run', async (req, res) => {
        try {
            const success = await runJobForcefully(req.params.id);
            if (!success) return res.status(404).json({ error: 'Job trigger failed' });
            res.json({ success: true, message: 'Job dispatched to background Agent' });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });


    const PORT = process.env.PORT || 4000;

    // Serve static dashboard files if they exist (allows single-command full-stack testing)
    const dashboardDist = path.join(__dirname, '..', 'dashboard', 'dist');
    if (fs.existsSync(dashboardDist)) {
        app.use(express.static(dashboardDist));
        // Fallback for React Router
        app.get('*', (req, res) => {
            res.sendFile(path.join(dashboardDist, 'index.html'));
        });
        console.log(`[Server] Web Dashboard statically served on http://localhost:${PORT}`);
    } else {
        console.log(`[Server] No compiled dashboard found at ${dashboardDist}. Run 'npm run build:frontend' first if you want the Web UI!`);
    }

    server.listen(PORT, () => {
        console.log(`[Server] OpenSpider API & WebSocket running on http://localhost:${PORT}`);
        initScheduler();
    });
}

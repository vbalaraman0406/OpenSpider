import express from 'express';
import { WebSocketServer, WebSocket } from 'ws';
import * as http from 'http';
import cors from 'cors';
import fs from 'node:fs';
import path from 'node:path';
import { ManagerAgent } from './agents/ManagerAgent';

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

                    // Send an immediate acknowledgement
                    ws.send(JSON.stringify({
                        type: 'chat_response',
                        data: '🕷️ OpenSpider is processing your request...',
                        timestamp: new Date().toISOString()
                    }));

                    // Process request
                    const response = await manager.processUserRequest(parsed.text);

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
        const message = args.map(a => typeof a === 'object' ? JSON.stringify(a) : a).join(' ');

        // Check if this log is a token usage event
        let isUsage = false;
        try {
            if (message.includes('"type":"usage"')) {
                const parsed = JSON.parse(message);
                if (parsed.type === 'usage') {
                    isUsage = true;
                    clients.forEach(client => {
                        if (client.readyState === WebSocket.OPEN) {
                            client.send(JSON.stringify({
                                type: 'usage',
                                data: parsed,
                                timestamp: new Date().toISOString()
                            }));
                        }
                    });
                }
            }
        } catch (e) {
            // Not JSON
        }

        if (!isUsage) {
            // Broadcast standard log to all dashboard clients
            clients.forEach(client => {
                if (client.readyState === WebSocket.OPEN) {
                    client.send(JSON.stringify({ type: 'log', data: message, timestamp: new Date().toISOString() }));
                }
            });
        }
    };

    // API Route to fetch current connection config
    app.get('/api/config', (req, res) => {
        const provider = process.env.DEFAULT_PROVIDER || 'ollama';
        res.json({ provider, status: 'running' });
    });

    // API Route to fetch active agents/skills
    app.get('/api/skills', (req, res) => {
        try {
            const skillsDir = path.join(process.cwd(), 'skills');
            if (!fs.existsSync(skillsDir)) return res.json({ skills: [] });

            const files = fs.readdirSync(skillsDir);
            res.json({ skills: files });
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
    });
}

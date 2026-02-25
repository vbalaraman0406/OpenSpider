import express from 'express';
import { WebSocketServer, WebSocket } from 'ws';
import * as http from 'http';
import cors from 'cors';
import fs from 'node:fs';
import path from 'node:path';

export function startServer() {
    const app = express();
    app.use(cors());
    app.use(express.json());

    const server = http.createServer(app);
    const wss = new WebSocketServer({ server });

    // Store connected clients
    const clients: Set<WebSocket> = new Set();

    wss.on('connection', (ws) => {
        clients.add(ws);
        console.log('[Server] Dashboard client connected');

        ws.on('close', () => clients.delete(ws));
    });

    // Override console.log to broadcast to WebSockets
    const originalLog = console.log;
    console.log = (...args: any[]) => {
        originalLog(...args);
        const message = args.map(a => typeof a === 'object' ? JSON.stringify(a) : a).join(' ');

        // Broadcast log to all dashboard clients
        clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(JSON.stringify({ type: 'log', data: message, timestamp: new Date().toISOString() }));
            }
        });
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
    server.listen(PORT, () => {
        console.log(`[Server] Openspider API & WebSocket running on http://localhost:${PORT}`);
    });
}

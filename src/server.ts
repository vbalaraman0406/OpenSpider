import express from 'express';
import { WebSocketServer, WebSocket } from 'ws';
import * as http from 'http';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import fs from 'node:fs';
import path from 'node:path';
import { ManagerAgent } from './agents/ManagerAgent';
import { getProvider } from './llm';
import { ChatMessage } from './llm/BaseProvider';
import { logMemory } from './memory';
import { initScheduler, runJobForcefully, activeCronJobs } from './scheduler';
import { logUsage, getUsageSummary } from './usage';
import { readJobsSync, writeJobsSync } from './CronStore';
import { PersonaShell } from './agents/PersonaShell';
import { LinkedInService } from './services/LinkedInService';
import gmailWebhookRouter from './webhooks/gmail';
import { apiKeyAuth, validateWsConnection } from './middleware/auth';
import { getManager } from './browser/manager';
import { registerRelay } from './browser/relayBridge';

export function startServer() {
    const app = express();

    // LOW: Security HTTP headers via Helmet
    // Adds X-Frame-Options, X-Content-Type-Options, Strict-Transport-Security,
    // X-XSS-Protection, Referrer-Policy, and Content-Security-Policy.
    // CSP is relaxed for localhost dashboard assets (inline scripts needed by Vite).
    app.use(helmet({
        hsts: false, // Disable Strict-Transport-Security to allow plain HTTP on local networks/Tailscale
        contentSecurityPolicy: {
            directives: {
                "upgrade-insecure-requests": null, // Disable forced HTTPS upgrades for HTTP IPs
                defaultSrc: ["'self'"],
                scriptSrc: ["'self'", "'unsafe-inline'", "'unsafe-eval'"],  // Vite/React requires this in dev
                styleSrc: ["'self'", "'unsafe-inline'"],
                imgSrc: ["'self'", "data:", "blob:"],
                connectSrc: ["'self'", "ws:", "wss:"], // Allow WebSocket on remote IPs natively
                fontSrc: ["'self'", "data:"],
                frameSrc: ["'none'"],
            },
        },
        crossOriginEmbedderPolicy: false, // Relax for WebSocket compatibility
    }));

    // SECURITY: Restrict CORS to localhost, private/Tailscale network IPs, and extensions
    app.use(cors({
        origin: (origin, callback) => {
            // Allow same-origin requests (no Origin header), localhost, private IPs (Tailscale 100.x, 192.168, etc), Tailscale MagicDNS, and chrome extensions
            if (!origin ||
                /^https?:\/\/(localhost|127\.0\.0\.1|100\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+)(:\d+)?$/.test(origin) ||
                /^https?:\/\/([a-zA-Z0-9.-]+)\.ts\.net(:\d+)?$/.test(origin) ||
                /^chrome-extension:\/\//.test(origin)) {
                callback(null, true);
            } else {
                callback(new Error('CORS: origin not allowed'));
            }
        },
        credentials: true,
    }));

    // Limit JSON body size to prevent memory exhaustion via large payloads
    app.use(express.json({ limit: '25mb' }));

    // MED-1: Rate limiting
    // General limiter: 120 req/min on all API routes (covers config reads, agent lists, etc.)
    const generalLimiter = rateLimit({
        windowMs: 60 * 1000,
        max: 120,
        standardHeaders: true,
        legacyHeaders: false,
        message: { error: 'Too many requests, please slow down.' },
    });
    // Strict limiter: 20 req/min on chat/voice/email — these spin up LLM calls and cost money
    const agentLimiter = rateLimit({
        windowMs: 60 * 1000,
        max: 20,
        standardHeaders: true,
        legacyHeaders: false,
        message: { error: 'Agent request rate limit exceeded. Max 20 requests per minute.' },
    });
    app.use('/api', generalLimiter);
    app.use('/api/chat', agentLimiter);
    app.use('/api/whatsapp/send', agentLimiter);
    app.use('/api/voice', agentLimiter);

    // SECURITY: Require API key on all /api/* routes.
    // /api/health is public (health checks don't need auth).
    // /hooks/* uses its own token — handled inside the gmail router.
    app.use('/api', (req, res, next) => {
        if (req.path === '/health') return next(); // public health check
        if (req.path === '/linkedin/auth' || req.path === '/linkedin/callback') return next(); // browser OAuth flow
        return apiKeyAuth(req, res, next);
    });

    const server = http.createServer(app);
    const wss = new WebSocketServer({ server });

    // Store connected clients
    const clients: Set<WebSocket> = new Set();

    // Persistent chat event buffer — survives gateway restarts by writing to disk
    // Stores the last 500 chat-relevant events so dashboard connections
    // instantly receive the full conversation context, even after restart.
    const CHAT_BUFFER_PATH = path.join(process.cwd(), 'workspace', 'chat_buffer.json');
    const MAX_BUFFER_SIZE = 500;

    // Dedicated conversation buffer — only stores [You]/[Agent] messages (not logs).
    // This prevents 500 log events from pushing out the actual conversation history.
    const CHAT_MESSAGES_PATH = path.join(process.cwd(), 'workspace', 'chat_messages.json');
    const MAX_CHAT_MESSAGES = 200;

    // Load persisted buffer from disk on startup
    let eventBuffer: Array<{ type: string; data: string; timestamp: string }> = [];
    try {
        if (fs.existsSync(CHAT_BUFFER_PATH)) {
            const raw = fs.readFileSync(CHAT_BUFFER_PATH, 'utf-8');
            const parsed = JSON.parse(raw);
            if (Array.isArray(parsed)) {
                eventBuffer = parsed.slice(-MAX_BUFFER_SIZE);
                // Fix: Purge cron system noise from event buffer too
                const beforeEventPurge = eventBuffer.length;
                eventBuffer = eventBuffer.filter(e =>
                    !e.data.startsWith('[CRON]') &&
                    !e.data.includes('Sending structured request') &&
                    !e.data.includes('Sending structured generation')
                );
                const eventPurged = beforeEventPurge - eventBuffer.length;
                console.log(`[Server] Restored ${eventBuffer.length} chat events from disk${eventPurged > 0 ? ` (purged ${eventPurged} cron noise)` : ''}.`);
            }
        }
    } catch (e) {
        console.warn('[Server] Could not restore chat buffer from disk, starting fresh.');
    }

    // Load persisted chat messages from disk
    let chatBuffer: Array<{ type: string; data: string; timestamp: string }> = [];
    try {
        if (fs.existsSync(CHAT_MESSAGES_PATH)) {
            const raw = fs.readFileSync(CHAT_MESSAGES_PATH, 'utf-8');
            const parsed = JSON.parse(raw);
            if (Array.isArray(parsed)) {
                // Evict messages older than 2 days
                const twoDaysAgo = Date.now() - 2 * 24 * 60 * 60 * 1000;
                const fresh = parsed.filter((m: any) => {
                    if (!m.timestamp) return true; // Keep messages without timestamps
                    return new Date(m.timestamp).getTime() > twoDaysAgo;
                });
                chatBuffer = fresh.slice(-MAX_CHAT_MESSAGES);
                // Fix: Purge cron system noise that may have leaked into the conversation buffer
                const beforePurge = chatBuffer.length;
                chatBuffer = chatBuffer.filter(m =>
                    !m.data.startsWith('[CRON]') &&
                    !m.data.includes('Sending structured request') &&
                    !m.data.includes('Sending structured generation')
                );
                const purged = beforePurge - chatBuffer.length;
                console.log(`[Server] Restored ${chatBuffer.length} conversation messages from disk (evicted ${parsed.length - fresh.length} older than 2 days${purged > 0 ? `, purged ${purged} cron noise entries` : ''}).`);
            }
        }
    } catch (e) {
        console.warn('[Server] Could not restore chat messages from disk, starting fresh.');
    }

    // Debounced disk persistence to avoid excessive I/O
    let bufferDirty = false;
    let flushTimer: ReturnType<typeof setTimeout> | null = null;
    let chatBufferDirty = false;
    let chatFlushTimer: ReturnType<typeof setTimeout> | null = null;

    const flushBufferToDisk = () => {
        if (bufferDirty) {
            try {
                fs.writeFileSync(CHAT_BUFFER_PATH, JSON.stringify(eventBuffer), 'utf-8');
                bufferDirty = false;
            } catch (e) {
                console.error('[Server] Failed to persist chat buffer:', e);
            }
        }
        if (chatBufferDirty) {
            try {
                fs.writeFileSync(CHAT_MESSAGES_PATH, JSON.stringify(chatBuffer), 'utf-8');
                chatBufferDirty = false;
            } catch (e) {
                console.error('[Server] Failed to persist chat messages:', e);
            }
        }
    };

    const bufferEvent = (event: { type: string; data: string; timestamp: string }) => {
        eventBuffer.push(event);
        if (eventBuffer.length > MAX_BUFFER_SIZE) {
            eventBuffer.shift(); // Remove oldest event
        }
        bufferDirty = true;

        // Debounce: flush to disk at most once every 2 seconds
        if (!flushTimer) {
            flushTimer = setTimeout(() => {
                flushBufferToDisk();
                flushTimer = null;
            }, 2000);
        }
    };

    // Buffer a user-facing conversation message (separate from log events)
    const bufferChatMessage = (event: { type: string; data: string; timestamp: string }) => {
        chatBuffer.push(event);
        if (chatBuffer.length > MAX_CHAT_MESSAGES) {
            chatBuffer.shift();
        }
        chatBufferDirty = true;
        if (!chatFlushTimer) {
            chatFlushTimer = setTimeout(() => {
                flushBufferToDisk();
                chatFlushTimer = null;
            }, 2000);
        }
    };

    // Also flush on process exit
    process.on('SIGINT', () => { flushBufferToDisk(); process.exit(); });
    process.on('SIGTERM', () => { flushBufferToDisk(); process.exit(); });

    const manager = new ManagerAgent();

    wss.on('connection', (ws, req) => {
        // SECURITY: Validate API key on WebSocket connect
        if (!validateWsConnection(req)) {
            console.warn('[Server] Rejected unauthenticated WebSocket connection');
            ws.close(1008, 'Unauthorized: missing or invalid apiKey');
            return;
        }

        clients.add(ws);

        // Replay conversation messages FIRST (dedicated chat buffer), then log events
        for (const msg of chatBuffer) {
            try { ws.send(JSON.stringify(msg)); } catch (e) { }
        }
        for (const event of eventBuffer) {
            try {
                ws.send(JSON.stringify(event));
            } catch (e) { }
        }

        console.log('[Server] Dashboard client connected');

        ws.on('message', async (messageData) => {
            try {
                const parsed = JSON.parse(messageData.toString());

                // Browser Relay extension registration
                if (parsed.type === 'relay_register') {
                    registerRelay(ws);
                    return;
                }

                if (parsed.type === 'chat') {
                    console.log(`\n\n[Web Chat] Received message: ${parsed.text}`);

                    // Buffer user message for conversation replay on reconnect
                    const userLabel = parsed.text + (parsed.images?.length > 0 ? ' 📎' : '');
                    bufferChatMessage({ type: 'chat', data: `[You] ${userLabel}`, timestamp: new Date().toISOString() });

                    // Log user message to session memory
                    logMemory('User', parsed.text, 'dashboard');

                    // Extract attached images (base64 data URLs) if present
                    const images: string[] = parsed.images || [];
                    if (images.length > 0) {
                        console.log(`[Web Chat] ${images.length} image(s) attached`);
                    }

                    // Save uploaded non-image files to workspace/uploads/ so Workers can access them
                    const uploadedFilePaths: string[] = [];
                    if (parsed.files && Array.isArray(parsed.files)) {
                        const uploadsDir = path.resolve(process.cwd(), 'workspace', 'uploads');
                        if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir, { recursive: true });

                        for (const file of parsed.files) {
                            try {
                                const { name, dataUrl } = file;
                                // Extract base64 data from data URL (format: data:mimetype;base64,XXXXX)
                                const base64Match = dataUrl.match(/^data:[^;]+;base64,(.+)$/);
                                if (base64Match) {
                                    // HIGH-5 FIX: Enforce file size limit (10MB decoded)
                                    const MAX_FILE_BYTES = 10 * 1024 * 1024;
                                    const base64Data = base64Match[1];
                                    if (base64Data.length > MAX_FILE_BYTES * 1.4) { // base64 expands ~33%
                                        console.warn(`[Web Chat] File too large, rejected: ${name}`);
                                        continue;
                                    }
                                    const buffer = Buffer.from(base64Data, 'base64');
                                    if (buffer.length > MAX_FILE_BYTES) {
                                        console.warn(`[Web Chat] Decoded file exceeds 10MB limit, rejected: ${name}`);
                                        continue;
                                    }

                                    // HIGH-5 FIX: Strip path separators and leading dots, use basename only
                                    const rawName = path.basename(name).replace(/^[\.]+/, '').replace(/[^a-zA-Z0-9._-]/g, '_') || 'upload';
                                    const resolvedPath = path.resolve(uploadsDir, rawName);
                                    // Path traversal guard
                                    if (!resolvedPath.startsWith(uploadsDir)) {
                                        console.warn(`[Web Chat] Filename traversal detected, rejected: ${name}`);
                                        continue;
                                    }

                                    fs.writeFileSync(resolvedPath, buffer);
                                    uploadedFilePaths.push(resolvedPath);
                                    console.log(`[Web Chat] Saved uploaded file: ${resolvedPath} (${buffer.length} bytes)`);
                                }
                            } catch (fileErr: any) {
                                console.error(`[Web Chat] Failed to save file:`, fileErr.message);
                            }
                        }
                    }

                    // Process request — ManagerAgent injects memory context internally,
                    // so we pass the raw user text to avoid double memory injection.
                    let userText = parsed.text;
                    if (uploadedFilePaths.length > 0) {
                        userText += `\n\n[UPLOADED FILES - saved to disk, Workers can read these paths directly]\n${uploadedFilePaths.map(p => `- ${p}`).join('\n')}`;
                    }
                    const response = await manager.processUserRequest(userText, images);

                    // Log agent response to session memory
                    logMemory('Agent', response, 'dashboard');

                    // Send final result
                    const chatResponseEvent = {
                        type: 'chat_response',
                        data: response,
                        timestamp: new Date().toISOString()
                    };
                    bufferEvent({ type: 'chat', data: `[Agent] ${response}`, timestamp: chatResponseEvent.timestamp });
                    bufferChatMessage({ type: 'chat', data: `[Agent] ${response}`, timestamp: chatResponseEvent.timestamp });
                    ws.send(JSON.stringify(chatResponseEvent));
                } else if (parsed.type === 'cancel') {
                    // User clicked the Cancel button in the dashboard
                    manager.cancel();
                    ws.send(JSON.stringify({
                        type: 'chat_response',
                        data: '⛔ Cancellation requested — the agent will stop at the next safe checkpoint.',
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
                if (message.includes('"type":"usage"') || message.includes('"type":"agent_flow"') || message.includes('"type":"cron_result"')) {
                    const parsed = JSON.parse(message);
                    if (parsed.type === 'usage' || parsed.type === 'agent_flow' || parsed.type === 'cron_result') {
                        isSpecialEvent = true;

                        // Skip broadcasting agent_flow events to dashboard during cron runs
                        // This prevents the UI from locking up when background cron jobs are executing
                        if (activeCronJobs > 0 && parsed.type === 'agent_flow') {
                            return; // Silently skip — don't send to WebSocket clients
                        }

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
                // MED-2: Strip sensitive data from log messages before broadcasting to WebSocket clients.
                // Raw console.log can include API keys, tokens, auth headers, and internal state.
                let safeMessage = message;
                // Redact API keys and bearer tokens from log lines
                safeMessage = safeMessage.replace(/([Xx]-[Aa][Pp][Ii]-[Kk]ey:\s*)([A-Za-z0-9]{16,})/g, 'X-API-Key: [REDACTED]');
                safeMessage = safeMessage.replace(/(Bearer\s+)([A-Za-z0-9._-]{16,})/g, 'Bearer [REDACTED]');
                safeMessage = safeMessage.replace(/("apiKey"\s*:\s*")([A-Za-z0-9._-]{16,})(")/g, '"apiKey": "[REDACTED]"');
                // Redact environment variable values that may appear in error traces
                safeMessage = safeMessage.replace(/([A-Z_]{6,}_KEY|[A-Z_]{6,}_TOKEN|[A-Z_]{6,}_SECRET)=[A-Za-z0-9._-]{8,}/g, '$1=[REDACTED]');

                // Broadcast standard log to all dashboard clients
                const logEvent = { type: 'log', data: safeMessage, timestamp: new Date().toISOString() };

                // Tag cron-originated logs so the dashboard can ignore them for typing state
                // Fix: Don't tag dashboard user/agent messages as cron — they're from the chat session
                if (activeCronJobs > 0 && !message.includes('[You]') && !message.includes('[Web Chat]')) {
                    logEvent.data = `[CRON] ${logEvent.data}`;
                }

                // Buffer chat-relevant events for page refresh persistence
                // Fix: Only buffer genuine user/agent conversation messages, not cron system logs
                // that happen to contain '[Agent]' (e.g. '[Agent] [AntigravityInternal] Sending structured request...')
                const isCronNoise = activeCronJobs > 0 && !message.includes('[You]') && !message.includes('[Web Chat]');
                if (!isCronNoise && (message.includes('[You]') || message.includes('[Agent]') || message.includes('[Web Chat]'))) {
                    bufferEvent(logEvent);
                    // Also persist to chatBuffer so messages survive dashboard refresh
                    // This captures WhatsApp and all channel messages, not just dashboard chat
                    bufferChatMessage(logEvent);
                }

                clients.forEach(client => {
                    if (client.readyState === WebSocket.OPEN) {
                        client.send(JSON.stringify(logEvent));
                    }
                });
            }
        });
    };

    // Health endpoint for dashboard status indicator & version badge
    app.get('/api/health', (req, res) => {
        const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'package.json'), 'utf-8'));
        const uptimeSec = Math.floor(process.uptime());
        const memMB = Math.round(process.memoryUsage().rss / 1024 / 1024);
        let waStatus: 'connected' | 'disconnected' = 'disconnected';
        try {
            const { getWhatsAppStatus } = require('./whatsapp');
            waStatus = getWhatsAppStatus();
        } catch { }
        const llmProvider = process.env.DEFAULT_PROVIDER || 'ollama';

        // Overall status: green = all OK, amber = degraded, red = critical
        let status: 'green' | 'amber' | 'red' = 'green';
        if (waStatus !== 'connected') status = 'amber';
        if (memMB > 1024) status = 'amber'; // >1GB memory = amber

        res.json({
            version: pkg.version,
            status,
            uptime: uptimeSec,
            memory: memMB,
            components: {
                whatsapp: waStatus,
                llm: llmProvider,
                server: 'running',
                scheduler: 'running'
            }
        });
    });

    // API Route to fetch current connection config
    app.get('/api/config', (req, res) => {
        const provider = process.env.DEFAULT_PROVIDER || 'ollama';
        res.json({ provider, status: 'running' });
    });

    // API Routes for WhatsApp
    const { getParticipatingGroups } = require('./whatsapp');

    app.get('/api/whatsapp/groups', async (req, res) => {
        try {
            const groups = await getParticipatingGroups();
            res.json({ groups });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    app.post('/api/whatsapp/send', async (req, res) => {
        try {
            const { sendWhatsAppMessage } = require('./whatsapp');
            const { to, text } = req.body;
            await sendWhatsAppMessage(`${to}@s.whatsapp.net`, text);
            res.json({ success: true, message: `Dispatched to ${to}` });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // Mount Gmail Webhook Routes
    app.use('/hooks', gmailWebhookRouter);

    // API Route to fetch chat persistence history
    app.get('/api/chat/history', (req, res) => {
        try {
            // Uses the same MEMORY_DIR logic as src/memory.ts
            const memoryDir = path.join(process.cwd(), 'workspace', 'memory');

            if (!fs.existsSync(memoryDir)) {
                return res.json([]);
            }

            // Only load files from the last 2 days to avoid flooding chat with old history
            const twoDaysAgo = new Date();
            twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);
            const cutoffDate = twoDaysAgo.toISOString().split('T')[0] || '1970-01-01'; // e.g. "2026-03-11"

            const files = fs.readdirSync(memoryDir)
                .filter(f => /^\d{4}-\d{2}-\d{2}\.md$/.test(f))
                .sort()
                .filter(f => f.replace('.md', '') >= cutoffDate); // Only last 2 days

            const history: any[] = [];

            // Process each file with its own date context
            for (const file of files) {
                // Extract date from filename (e.g. "2026-03-12.md" → "2026-03-12")
                const fileDate = file.replace('.md', '');
                const logContent = fs.readFileSync(path.join(memoryDir, file), 'utf-8');
                // Skip [COMPACTED] summary blocks — they're internal agent bookkeeping
                const logLines = logContent.split('\n').filter(line => !line.includes('[COMPACTED]'));

                let currentTimestamp = "";
                let currentSender = "";
                let currentText: string[] = [];

                const pushBlock = () => {
                    if (!currentTimestamp) return;
                    let validIsoDate = "";
                    try {
                        const [timePart, modifier] = currentTimestamp.split(' ');
                        let [hoursStr, minutesStr, secondsStr] = (timePart || "").split(':');

                        let hours = parseInt(hoursStr || "0", 10);
                        const minutes = parseInt(minutesStr || "0", 10);
                        const seconds = parseInt(secondsStr || "0", 10);

                        if (modifier === 'PM' && hours < 12) hours += 12;
                        if (modifier === 'AM' && hours === 12) hours = 0;

                        // Use the DATE from the filename, not today's date
                        const d = new Date(`${fileDate}T00:00:00`);
                        d.setHours(hours, minutes, seconds, 0);
                        validIsoDate = d.toISOString();
                    } catch {
                        validIsoDate = new Date().toISOString();
                    }

                    history.push({
                        type: 'chat',
                        data: `[${currentSender === 'User' ? 'You' : 'Agent'}] ${currentText.join('\n').trim()}`,
                        timestamp: validIsoDate
                    });
                };

                for (const line of logLines) {
                    const match = line.match(/^\[(.*?)\] \*\*(.*?)\*\*.*?: (.*)/);

                    if (match) {
                        pushBlock();
                        currentTimestamp = match[1] || "";
                        currentSender = match[2] || "";
                        currentText = [match[3] || ""];
                    } else if (currentTimestamp) {
                        currentText.push(line);
                    }
                }
                // Push the final dangling block for this file
                pushBlock();
            }

            res.json(history);
        } catch (e: any) {
            console.error("Chat History Error:", e);
            res.status(500).json({ error: e.message });
        }
    });

    const whatsappConfigPath = path.join(process.cwd(), 'workspace', 'whatsapp_config.json');

    app.get('/api/whatsapp/config', (req, res) => {
        try {
            if (!fs.existsSync(whatsappConfigPath)) {
                return res.json({ enabled: false, dmPolicy: "allowlist", allowedDMs: [], groupPolicy: "disabled", allowedGroups: [], botMode: "mention" });
            }
            const config = JSON.parse(fs.readFileSync(whatsappConfigPath, 'utf-8'));
            res.json(config);
        } catch (e: any) {
            res.status(500).json({ error: Object.keys(e).length ? JSON.stringify(e) : e.message });
        }
    });

    app.post('/api/whatsapp/config', (req, res) => {
        try {
            const { dmPolicy, allowedDMs, groupPolicy, allowedGroups, botMode } = req.body;

            // Validate incoming payload shapes simply
            if (typeof dmPolicy !== 'string' || !Array.isArray(allowedDMs)) {
                return res.status(400).json({ error: "Invalid schema for DM constraints." });
            }

            // Preserve existing fields (especially 'enabled') that aren't part of security settings
            let existingConfig: any = {};
            try {
                if (fs.existsSync(whatsappConfigPath)) {
                    existingConfig = JSON.parse(fs.readFileSync(whatsappConfigPath, 'utf-8'));
                }
            } catch (e) { }

            const newConfig = {
                ...existingConfig, // Preserve enabled, owner phone, etc.
                dmPolicy,
                allowedDMs,
                groupPolicy: groupPolicy || 'disabled',
                allowedGroups: allowedGroups || [],
                botMode: botMode || 'mention'
            };

            fs.writeFileSync(whatsappConfigPath, JSON.stringify(newConfig, null, 2), 'utf-8');
            res.json({ success: true, config: newConfig });
        } catch (e: any) {
            res.status(500).json({ error: Object.keys(e).length ? JSON.stringify(e) : e.message });
        }
    });

    // Map a WhatsApp LID to a phone number in the allowlist
    // Used when Baileys can't automatically resolve LID↔phone mappings
    app.post('/api/whatsapp/lid-map', (req, res) => {
        try {
            const { lid, phone } = req.body;
            if (!lid || !phone) {
                return res.status(400).json({ error: "Both 'lid' and 'phone' are required." });
            }

            const cleanLid = String(lid).replace(/\D/g, '');
            const cleanPhone = String(phone).replace(/\D/g, '');

            if (!fs.existsSync(whatsappConfigPath)) {
                return res.status(404).json({ error: "WhatsApp config not found. Configure WhatsApp first." });
            }

            const config = JSON.parse(fs.readFileSync(whatsappConfigPath, 'utf-8'));
            const dms = config.allowedDMs || [];
            let mapped = false;

            // Find matching phone entry and add LID
            for (let i = 0; i < dms.length; i++) {
                const entry = dms[i];
                const entryNum = (typeof entry === 'string' ? entry : entry?.number || '').replace(/\D/g, '');
                if (entryNum === cleanPhone) {
                    if (typeof dms[i] === 'string') {
                        // Upgrade from legacy string to object format
                        dms[i] = { number: dms[i], lid: cleanLid, mode: 'always' };
                    } else {
                        dms[i].lid = cleanLid;
                    }
                    mapped = true;
                    break;
                }
            }

            if (!mapped) {
                // Phone not in allowlist — add it with LID
                dms.push({ number: cleanPhone, lid: cleanLid, mode: 'always' });
            }

            config.allowedDMs = dms;
            fs.writeFileSync(whatsappConfigPath, JSON.stringify(config, null, 2), 'utf-8');

            // Update in-memory caches AND clear from pending notifications
            try {
                const { addLidMappingFromApi } = require('./whatsapp');
                addLidMappingFromApi(cleanLid, cleanPhone);
            } catch (e) { /* whatsapp module may not be loaded in all contexts */ }

            // Also update lid_cache.json for the in-memory cache
            try {
                const rootDir = __dirname.endsWith('src') || __dirname.endsWith('dist') ? path.join(__dirname, '..') : __dirname;
                const cachePath = path.join(rootDir, 'workspace', 'lid_cache.json');
                let cache: Record<string, string> = {};
                if (fs.existsSync(cachePath)) cache = JSON.parse(fs.readFileSync(cachePath, 'utf-8'));
                cache[cleanLid] = cleanPhone;
                fs.writeFileSync(cachePath, JSON.stringify(cache, null, 2), 'utf-8');
            } catch (e) { /* non-critical */ }

            console.log(`[API] LID mapped: ${cleanLid} → ${cleanPhone}`);
            res.json({ success: true, message: `LID ${cleanLid} mapped to phone ${cleanPhone}.` });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // List all LID↔phone mappings (for dashboard UI)
    app.get('/api/whatsapp/lid-mappings', (req, res) => {
        try {
            const { getLidMappings } = require('./whatsapp');
            const mappings = getLidMappings();

            // Also include LID fields from whatsapp_config.json allowedDMs
            if (fs.existsSync(whatsappConfigPath)) {
                const config = JSON.parse(fs.readFileSync(whatsappConfigPath, 'utf-8'));
                const dms = config.allowedDMs || [];
                for (const entry of dms) {
                    if (typeof entry === 'object' && entry.lid && entry.number) {
                        const cleanLid = String(entry.lid).replace(/\D/g, '');
                        const cleanPhone = String(entry.number).replace(/\D/g, '');
                        if (cleanLid && cleanPhone && !mappings[cleanLid]) {
                            mappings[cleanLid] = cleanPhone;
                        }
                    }
                }
            }

            res.json({ mappings });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // Get pending (unmapped) LIDs that tried to DM
    app.get('/api/whatsapp/lid-pending', (req, res) => {
        try {
            const { getPendingLids } = require('./whatsapp');
            const pending = getPendingLids();
            res.json({ pending });
        } catch (e: any) {
            res.json({ pending: [] }); // Gracefully degrade if whatsapp module not loaded
        }
    });

    // Remove a LID mapping
    app.delete('/api/whatsapp/lid-map/:lid', (req, res) => {
        try {
            const lid = req.params.lid.replace(/\D/g, '');
            if (!lid) return res.status(400).json({ error: 'Invalid LID' });

            const { removeLidMapping } = require('./whatsapp');
            removeLidMapping(lid);

            // Also remove from whatsapp_config.json allowedDMs[].lid
            if (fs.existsSync(whatsappConfigPath)) {
                const config = JSON.parse(fs.readFileSync(whatsappConfigPath, 'utf-8'));
                const dms = config.allowedDMs || [];
                for (const entry of dms) {
                    if (typeof entry === 'object' && entry.lid && String(entry.lid).replace(/\D/g, '') === lid) {
                        delete entry.lid;
                    }
                }
                config.allowedDMs = dms;
                fs.writeFileSync(whatsappConfigPath, JSON.stringify(config, null, 2), 'utf-8');
            }

            // Also remove from lid_cache.json
            try {
                const rootDir = __dirname.endsWith('src') || __dirname.endsWith('dist') ? path.join(__dirname, '..') : __dirname;
                const cachePath = path.join(rootDir, 'workspace', 'lid_cache.json');
                if (fs.existsSync(cachePath)) {
                    const cache = JSON.parse(fs.readFileSync(cachePath, 'utf-8'));
                    delete cache[lid];
                    fs.writeFileSync(cachePath, JSON.stringify(cache, null, 2), 'utf-8');
                }
            } catch (e) { /* non-critical */ }

            console.log(`[API] LID mapping removed: ${lid}`);
            res.json({ success: true, message: `LID ${lid} mapping removed.` });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // --- EMAIL CONFIG ENDPOINTS ---
    const emailConfigPath = path.join(process.cwd(), 'workspace', 'email_config.json');

    app.get('/api/email/config', (req, res) => {
        try {
            if (!fs.existsSync(emailConfigPath)) {
                return res.json({ cronResultsTo: '', vendorEmailTo: '' });
            }
            const config = JSON.parse(fs.readFileSync(emailConfigPath, 'utf-8'));
            res.json(config);
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    app.post('/api/email/config', (req, res) => {
        try {
            const { cronResultsTo, vendorEmailTo } = req.body;

            // Basic email validation (allow empty = unset)
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (cronResultsTo && !emailRegex.test(cronResultsTo)) {
                return res.status(400).json({ error: 'Invalid cronResultsTo email address.' });
            }
            if (vendorEmailTo && !emailRegex.test(vendorEmailTo)) {
                return res.status(400).json({ error: 'Invalid vendorEmailTo email address.' });
            }

            const newConfig = {
                cronResultsTo: cronResultsTo || '',
                vendorEmailTo: vendorEmailTo || ''
            };

            // Ensure workspace directory exists
            const wsDir = path.join(process.cwd(), 'workspace');
            if (!fs.existsSync(wsDir)) fs.mkdirSync(wsDir, { recursive: true });

            fs.writeFileSync(emailConfigPath, JSON.stringify(newConfig, null, 2), 'utf-8');

            console.log(`[API] Email config saved: cronResultsTo=${newConfig.cronResultsTo}, vendorEmailTo=${newConfig.vendorEmailTo}`);
            res.json({ success: true, config: newConfig });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // API Route to fetch aggregated usage summary
    app.get('/api/usage', (req, res) => {
        try {
            const days = parseInt(req.query.days as string) || 30;
            res.json(getUsageSummary(days));
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // --- VOICE CONFIG ENDPOINTS ---
    const voiceConfigPath = path.join(process.cwd(), 'workspace', 'voice_config.json');

    app.get('/api/voice/config', (req, res) => {
        try {
            if (!fs.existsSync(voiceConfigPath)) {
                return res.json({
                    voiceId: process.env.ELEVENLABS_VOICE_ID || '21m00Tcm4TlvDq8ikWAM',
                    voiceName: 'Rachel',
                    elevenlabsApiKey: process.env.ELEVENLABS_API_KEY || '',
                    whisperModel: process.env.WHISPER_MODEL || 'base'
                });
            }
            const config = JSON.parse(fs.readFileSync(voiceConfigPath, 'utf-8'));
            res.json(config);
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    app.post('/api/voice/config', (req, res) => {
        try {
            const { voiceId, voiceName, elevenlabsApiKey, whisperModel } = req.body;
            const newConfig = {
                voiceId: voiceId || '21m00Tcm4TlvDq8ikWAM',
                voiceName: voiceName || 'Rachel',
                elevenlabsApiKey: elevenlabsApiKey || '',
                whisperModel: whisperModel || 'base'
            };

            // Ensure workspace directory exists
            const wsDir = path.join(process.cwd(), 'workspace');
            if (!fs.existsSync(wsDir)) fs.mkdirSync(wsDir, { recursive: true });

            fs.writeFileSync(voiceConfigPath, JSON.stringify(newConfig, null, 2), 'utf-8');

            // Also update env vars in memory so they take effect immediately without restart
            process.env.ELEVENLABS_VOICE_ID = newConfig.voiceId;
            process.env.ELEVENLABS_API_KEY = newConfig.elevenlabsApiKey;
            process.env.WHISPER_MODEL = newConfig.whisperModel;

            // SECURITY: Do NOT return the full API key in the response — return masked version.
            res.json({
                success: true,
                config: {
                    voiceId: newConfig.voiceId,
                    voiceName: newConfig.voiceName,
                    elevenlabsApiKey: newConfig.elevenlabsApiKey
                        ? `${newConfig.elevenlabsApiKey.substring(0, 6)}${'*'.repeat(Math.max(0, newConfig.elevenlabsApiKey.length - 6))}`
                        : '',
                    whisperModel: newConfig.whisperModel,
                }
            });
        } catch (e: any) {
            res.status(500).json({ error: 'Internal server error' });
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

    // API Route to inject cookies into the OpenSpider browser
    // CORS preflight: Allow cookie export from ANY origin (endpoint is API-key protected)
    app.options('/api/v1/browser/cookies', (req, res) => {
        res.setHeader('Access-Control-Allow-Origin', req.headers.origin || '*');
        res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-api-key');
        res.setHeader('Access-Control-Allow-Credentials', 'true');
        res.status(204).end();
    });
    app.post('/api/v1/browser/cookies', (req, res, next) => {
        // Diagnostic log: confirm cookie export request reached the server
        console.log(`[Server] Cookie export request received from ${req.ip} (${req.headers.origin || 'no origin'})`);
        // Override CORS for this specific endpoint
        res.setHeader('Access-Control-Allow-Origin', req.headers.origin || '*');
        res.setHeader('Access-Control-Allow-Credentials', 'true');
        next();
    }, apiKeyAuth, async (req, res) => {
        try {
            const { cookies } = req.body;
            if (!cookies || !Array.isArray(cookies)) {
                return res.status(400).json({ error: "Invalid cookies array provided." });
            }

            // 1. ALWAYS persist cookies to disk first (works even without browser)
            const cookieFile = path.join(process.cwd(), 'workspace', 'browser_cookies.json');
            let existing: any[] = [];
            try {
                if (fs.existsSync(cookieFile)) {
                    existing = JSON.parse(fs.readFileSync(cookieFile, 'utf-8'));
                }
            } catch { }

            // Merge: update existing cookies by domain+name+path, add new ones
            for (const c of cookies) {
                const key = `${c.domain}|${c.name}|${c.path || '/'}`;
                const idx = existing.findIndex((e: any) => `${e.domain}|${e.name}|${e.path || '/'}` === key);
                if (idx >= 0) existing[idx] = c;
                else existing.push(c);
            }

            fs.writeFileSync(cookieFile, JSON.stringify(existing, null, 2));
            console.log(`[Server] Persisted ${cookies.length} cookies to disk (total: ${existing.length})`);

            // 2. Optionally inject into browser if one is already running
            let injected = false;
            try {
                const manager = getManager();
                await manager.injectCookies('default', cookies);
                injected = true;
            } catch (browserErr: any) {
                console.log(`[Server] Browser not running — cookies saved to disk only (will auto-inject on next launch)`);
            }

            res.json({ success: true, count: cookies.length, persisted: existing.length, injected });
        } catch (e: any) {
            console.error('[Server] Failed to persist cookies:', e);
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
    const getAgents = () => {
        const { PersonaShell } = require('./agents/PersonaShell');
        const agentsDir = path.join(process.cwd(), 'workspace', 'agents');
        const agents: any[] = [];

        if (!fs.existsSync(agentsDir)) {
            fs.mkdirSync(agentsDir, { recursive: true });
        }

        const agentFolders = fs.readdirSync(agentsDir)
            .filter(f => fs.statSync(path.join(agentsDir, f)).isDirectory())
            .sort();

        for (const agentId of agentFolders) {
            const shell = new PersonaShell(agentId);
            const caps = shell.getCapabilities() || {};
            agents.push({
                id: agentId,
                name: caps.name || agentId,
                role: caps.role || 'Unspecified',
                status: caps.status === 'stopped' ? 'red' : 'emerald',
                initial: caps.emoji || (caps.name || agentId).charAt(0).toUpperCase(),
                emoji: caps.emoji || '',
                color: caps.color || 'fuchsia',
                model: caps.model || process.env.DEFAULT_PROVIDER || 'ollama',
                prompt: shell.compileSystemPrompt(),
                skills: caps.allowedTools || [],
                pillars: {
                    identity: shell.getIdentity(),
                    soul: shell.getSoul(),
                    userContext: shell.getUserContext(),
                    capabilities: JSON.stringify(caps, null, 2)
                }
            });
        }
        return agents;
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
            const { name, role, model, color, prompt } = req.body;
            const id = name.toLowerCase().replace(/[^a-z0-9]/g, '');

            const agentDir = path.join(process.cwd(), 'workspace', 'agents', id);
            if (fs.existsSync(agentDir)) {
                return res.status(400).json({ error: `Agent "${id}" already exists. Choose a different name.` });
            }

            // Use PersonaShell.bootstrapAgent for consistent pillar file creation
            PersonaShell.bootstrapAgent(id, name, role, prompt || '');

            // Override CAPABILITIES.json with any extra fields from the UI (color, model)
            const capsPath = path.join(agentDir, 'CAPABILITIES.json');
            const caps = JSON.parse(fs.readFileSync(capsPath, 'utf-8'));
            if (color) caps.color = color;
            if (model) caps.model = model;
            fs.writeFileSync(capsPath, JSON.stringify(caps, null, 4));

            res.json({ success: true, agent: { id } });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // API Route to manually update agent pillars
    app.put('/api/agents/:id', (req, res) => {
        try {
            const id = req.params.id;
            const { identity, soul, userContext, capabilities } = req.body;
            const agentsDir = path.resolve(process.cwd(), 'workspace', 'agents');
            const agentDir = path.resolve(agentsDir, id);

            // SECURITY FIX (HIGH-4): Path traversal protection
            if (!agentDir.startsWith(agentsDir + path.sep)) {
                return res.status(403).json({ error: 'Forbidden: Path traversal detected' });
            }

            if (!fs.existsSync(agentDir)) return res.status(404).json({ error: 'Agent not found' });

            if (identity !== undefined) fs.writeFileSync(path.join(agentDir, 'IDENTITY.md'), identity);
            if (soul !== undefined) fs.writeFileSync(path.join(agentDir, 'SOUL.md'), soul);
            if (userContext !== undefined) fs.writeFileSync(path.join(agentDir, 'USER.md'), userContext);
            if (capabilities !== undefined) fs.writeFileSync(path.join(agentDir, 'CAPABILITIES.json'), capabilities);

            res.json({ success: true });
        } catch (e: any) {
            res.status(500).json({ error: 'Internal server error' });
        }
    });

    // API Route to assign a skill to an agent
    app.post('/api/agents/:id/skills', (req, res) => {
        try {
            const agentId = req.params.id;
            const { skill } = req.body;
            if (!skill) return res.status(400).json({ error: 'Skill is required' });

            const agentsDir = path.resolve(process.cwd(), 'workspace', 'agents');
            const agentDir = path.resolve(agentsDir, agentId);

            // SECURITY FIX (HIGH-4): Path traversal protection
            if (!agentDir.startsWith(agentsDir + path.sep)) {
                return res.status(403).json({ error: 'Forbidden: Path traversal detected' });
            }

            if (!fs.existsSync(agentDir)) return res.status(404).json({ error: 'Agent not found' });

            const capsPath = path.join(agentDir, 'CAPABILITIES.json');
            let caps: any = {};
            if (fs.existsSync(capsPath)) {
                caps = JSON.parse(fs.readFileSync(capsPath, 'utf-8'));
            }

            if (!caps.allowedTools) caps.allowedTools = [];
            if (!caps.allowedTools.includes(skill)) {
                caps.allowedTools.push(skill);
                fs.writeFileSync(capsPath, JSON.stringify(caps, null, 2));
            }

            res.json({ success: true });
        } catch (e: any) {
            res.status(500).json({ error: 'Internal server error' });
        }
    });

    // API Route to delete an agent (except manager)
    app.delete('/api/agents/:id', (req, res) => {
        try {
            const id = req.params.id;

            // Never allow deleting the manager agent
            if (id === 'manager') {
                return res.status(403).json({ error: 'Cannot delete the Manager agent — it is a core system component.' });
            }

            const agentsDir = path.resolve(process.cwd(), 'workspace', 'agents');
            const agentDir = path.resolve(agentsDir, id);

            // Path traversal protection
            if (!agentDir.startsWith(agentsDir)) {
                return res.status(403).json({ error: 'Forbidden Path Traversal Detected' });
            }

            if (!fs.existsSync(agentDir)) {
                return res.status(404).json({ error: 'Agent not found' });
            }

            // Recursively delete the agent directory
            fs.rmSync(agentDir, { recursive: true, force: true });
            console.log(`[Server] Deleted agent: ${id}`);

            res.json({ success: true, message: `Agent "${id}" permanently deleted.` });
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // --- CRON JOBS REST ENDPOINTS ---
    const cronJobsPath = path.join(process.cwd(), 'workspace', 'cron_jobs.json');

    // --- SYSTEM PROCESS ENDPOINTS ---
    app.get('/api/processes', (req, res) => {
        try {
            const { execSync } = require('child_process');
            // Fetch running node strings, and optionally PM2 or Python if we wanted to filter.
            // For now, let's grab all node/python processes to see what OpenSpider agents or webhooks are running.
            const stdout = execSync('ps -ef | grep -E "node|python|playwright" | grep -v grep').toString();

            const processes = stdout.split('\n').filter((l: string) => l.trim().length > 0).map((line: string) => {
                // Typical ps -ef output: UID PID PPID C STIME TTY TIME CMD
                const parts = line.trim().split(/\s+/);
                return {
                    uid: parts[0],
                    pid: parts[1],
                    ppid: parts[2],
                    stime: parts[4],
                    time: parts[6],
                    cmd: parts.slice(7).join(' ')
                };
            });
            res.json(processes);
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    app.delete('/api/processes/:pid', (req, res) => {
        try {
            const pid = parseInt(req.params.pid, 10);
            if (isNaN(pid) || pid <= 0) return res.status(400).json({ error: 'Invalid PID' });
            // SECURITY: Validate PID is in a safe range to prevent kill-1 or kill-0 edge cases.
            // Also use spawnSync instead of execSync string interpolation to prevent any injection.
            if (pid <= 1 || pid > 4194304) return res.status(400).json({ error: 'PID out of safe range' });
            const { spawnSync } = require('child_process');
            const result = spawnSync('kill', ['-9', String(pid)], { timeout: 3000 });
            if (result.status !== 0 && result.error) {
                return res.status(500).json({ error: 'Failed to terminate process' });
            }
            res.json({ success: true, message: `Terminated process ${pid}` });
        } catch (e: any) {
            res.status(500).json({ error: 'Internal server error' });
        }
    });

    // ─── LinkedIn OAuth Routes ───────────────────────────────────
    app.get('/api/linkedin/auth', (req, res) => {
        try {
            const linkedin = LinkedInService.getInstance();
            const authUrl = linkedin.getAuthUrl();
            res.redirect(authUrl);
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    app.get('/api/linkedin/callback', async (req, res) => {
        try {
            const code = req.query.code as string;
            if (!code) return res.status(400).send('Missing authorization code');

            const linkedin = LinkedInService.getInstance();
            const result = await linkedin.handleCallback(code);

            if (result.success) {
                res.send(`
                    <html><body style="background:#0f172a;color:#e2e8f0;font-family:system-ui;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
                        <div style="text-align:center">
                            <h1 style="color:#38bdf8">✅ LinkedIn Connected!</h1>
                            <p>Authenticated as <strong>${result.name}</strong></p>
                            <p style="color:#64748b">You can close this window and return to OpenSpider.</p>
                        </div>
                    </body></html>
                `);
            } else {
                res.status(500).send(`LinkedIn auth failed: ${result.error}`);
            }
        } catch (e: any) {
            res.status(500).send(`OAuth error: ${e.message}`);
        }
    });

    app.post('/api/linkedin/post', async (req, res) => {
        try {
            const { text } = req.body;
            if (!text) return res.status(400).json({ error: 'text is required' });

            const linkedin = LinkedInService.getInstance();
            const result = await linkedin.createPost(text);

            if (result.success) {
                res.json({ success: true, postId: result.postId });
            } else {
                res.status(500).json({ error: result.error });
            }
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    app.get('/api/linkedin/status', (req, res) => {
        try {
            const linkedin = LinkedInService.getInstance();
            res.json(linkedin.getTokenStatus());
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    // ─── Cron Routes ─────────────────────────────────────────────
    app.get('/api/cron', (req, res) => {
        try {
            const jobs = readJobsSync();
            res.json(jobs);
        } catch (e: any) {
            res.status(500).json({ error: e.message });
        }
    });

    app.post('/api/cron', (req, res) => {
        try {
            const { description, prompt, intervalHours, agentId, preferredTime } = req.body;

            // SECURITY: Input validation
            if (!description || !prompt) return res.status(400).json({ error: 'description and prompt are required.' });
            if (typeof description !== 'string' || description.length > 200) return res.status(400).json({ error: 'description must be a string under 200 chars.' });
            if (typeof prompt !== 'string' || prompt.length > 2000) return res.status(400).json({ error: 'prompt must be a string under 2000 chars.' });

            let jobs = readJobsSync();

            // SECURITY: Cap the maximum number of cron jobs to prevent resource exhaustion
            const MAX_JOBS = 20;
            if (jobs.length >= MAX_JOBS) {
                return res.status(429).json({ error: `Maximum of ${MAX_JOBS} cron jobs allowed. Delete an existing job first.` });
            }

            // SECURITY: Enforce a minimum interval floor to prevent LLM spam attacks
            const MIN_INTERVAL_HOURS = 0.25; // 15 minutes minimum
            const parsedInterval = Number(intervalHours);
            const safeInterval = (!parsedInterval || parsedInterval < MIN_INTERVAL_HOURS)
                ? 24  // Default to 24h if invalid or too short
                : parsedInterval;

            // SECURITY: Validate preferredTime format (HH:MM) to prevent injection
            const safePreferredTime = preferredTime && /^([01]?\d|2[0-3]):[0-5]\d$/.test(String(preferredTime))
                ? String(preferredTime)
                : undefined;

            const newJob: any = {
                id: 'cron-' + Math.random().toString(36).substr(2, 9),
                description: description.trim(),
                prompt: prompt.trim(),
                intervalHours: safeInterval,
                lastRunTimestamp: safePreferredTime ? 0 : Date.now(),
                agentId: agentId || 'gateway',
                status: 'enabled'
            };
            if (safePreferredTime) newJob.preferredTime = safePreferredTime;

            jobs.push(newJob);
            writeJobsSync(jobs);
            res.json({ success: true, job: newJob });
        } catch (e: any) {
            res.status(500).json({ error: 'Internal server error' });
        }
    });

    app.delete('/api/cron/:id', (req, res) => {
        try {
            let jobs = readJobsSync();
            jobs = jobs.filter((j: any) => j.id !== req.params.id);
            writeJobsSync(jobs);
            res.json({ success: true });
        } catch (e: any) {
            res.status(500).json({ error: 'Internal server error' });
        }
    });

    app.put('/api/cron/:id', (req, res) => {
        try {
            let jobs = readJobsSync();
            const jobIndex = jobs.findIndex((j: any) => j.id === req.params.id);

            if (jobIndex === -1) return res.status(404).json({ error: 'Job not found' });

            jobs[jobIndex] = { ...jobs[jobIndex], ...req.body };
            writeJobsSync(jobs);
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


    const PORT = process.env.PORT || 4001;

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

    // LOW: Global error handler — prevents stack traces and internal error details
    // from leaking to clients. All unhandled Express errors return a generic 500.
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
        console.error('[Server] Unhandled error:', err.message || err);
        res.status(err.status || 500).json({ error: 'Internal server error' });
    });

    server.listen(PORT, () => {
        console.log(`[Server] OpenSpider API & WebSocket running on http://localhost:${PORT}`);
        initScheduler();
    });
}

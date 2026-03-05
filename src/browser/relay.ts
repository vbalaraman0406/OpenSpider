import { WebSocketServer, WebSocket } from 'ws';
import * as http from 'http';
import * as url from 'node:url';

interface RelayConfig {
    port: number;
    gatewayToken?: string;
}

export class BrowserRelay {
    private server: http.Server | null = null;
    private wss: WebSocketServer | null = null;

    // Using a simple 1:1 mapping for the relay: One active Chrome tab to One Agent connection
    private agentClient: WebSocket | null = null;
    private chromeClient: WebSocket | null = null;

    constructor(private config: RelayConfig) { }

    start() {
        this.server = http.createServer((req, res) => {
            res.writeHead(200);
            res.end("OpenSpider Browser Relay running.\n");
        });

        this.wss = new WebSocketServer({ server: this.server });

        this.wss.on('connection', (ws, req) => {
            const reqUrl = url.parse(req.url || '', true);
            const token = reqUrl.query.token as string;

            // Simple Auth Check (Only if gateway Token is configured)
            if (this.config.gatewayToken && token !== this.config.gatewayToken) {
                console.warn("[Relay] Rejecting connection: Invalid or missing token.");
                ws.close(4003, "Forbidden");
                return;
            }

            // Identify if this is the Chrome Extension attaching or the Playwright Agent attaching
            // Playwright usually connects to /devtools/browser or just / (we can distinguish by origin/headers, or just first-come-first-serve for our simple 1:1 pipeline)
            const isChromeExtension = req.headers['origin']?.startsWith('chrome-extension://') || reqUrl.query.role === 'extension';

            if (isChromeExtension || token) {
                console.log("[Relay] Chrome Extension Connected.");
                if (this.chromeClient) {
                    console.warn("[Relay] Overwriting existing Chrome Extension connection.");
                    this.chromeClient.close();
                }
                this.chromeClient = ws;

                ws.on('message', (message) => {
                    // Pipe Chrome -> Agent
                    if (this.agentClient && this.agentClient.readyState === WebSocket.OPEN) {
                        this.agentClient.send(message);
                    }
                });

                ws.on('close', () => {
                    console.log("[Relay] Chrome Extension Disconnected.");
                    this.chromeClient = null;
                });
            } else {
                console.log("[Relay] Playwright Agent Connected.");
                if (this.agentClient) {
                    console.warn("[Relay] Overwriting existing Agent connection.");
                    this.agentClient.close();
                }
                this.agentClient = ws;

                ws.on('message', (message) => {
                    // Pipe Agent -> Chrome
                    if (this.chromeClient && this.chromeClient.readyState === WebSocket.OPEN) {
                        this.chromeClient.send(message);
                    } else {
                        console.warn("[Relay] Agent sent command but Chrome Extension is not attached in the browser!");
                    }
                });

                ws.on('close', () => {
                    console.log("[Relay] Playwright Agent Disconnected.");
                    this.agentClient = null;
                });
            }
        });

        this.server.listen(this.config.port, '127.0.0.1', () => {
            console.log(`[BrowserRelay] Listening for CDP proxy connections on ws://127.0.0.1:${this.config.port}`);
        });
    }

    stop() {
        if (this.wss) this.wss.close();
        if (this.server) this.server.close();
        this.agentClient = null;
        this.chromeClient = null;
    }
}

// Auto-start if run directly for standalone usage, or wait to be imported by the orchestrator
if (require.main === module) {
    const port = parseInt(process.env.OPENSPIDER_RELAY_PORT || '18792', 10);
    const token = process.env.DASHBOARD_API_KEY;
    const relay = new BrowserRelay({ port, ...(token ? { gatewayToken: token } : {}) });
    relay.start();
}

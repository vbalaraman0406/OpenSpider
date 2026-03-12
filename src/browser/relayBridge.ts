/**
 * RelayBridge: Bridge between BrowserTool and the Chrome Browser Relay extension.
 * 
 * When the extension connects via WebSocket and sends a 'relay_register' message,
 * this bridge enables the BrowserTool to send CDP commands to the extension and
 * receive responses — without needing a direct CDP connection.
 * 
 * Architecture:
 *   BrowserTool → RelayBridge.sendCommand() → WebSocket → Extension → chrome.debugger → Chrome
 */

import { WebSocket } from 'ws';

let relayClient: WebSocket | null = null;
let commandId = 1000;
const pendingCommands = new Map<number, { resolve: (result: any) => void; reject: (err: Error) => void }>();

/**
 * Register a WebSocket client as the browser relay extension.
 */
export function registerRelay(ws: WebSocket): void {
    relayClient = ws;
    console.log('[RelayBridge] 🔗 Browser relay extension connected.');

    // Listen for CDP responses from the extension
    ws.on('message', (data) => {
        try {
            const msg = JSON.parse(data.toString());
            // CDP responses have an 'id' field matching the command we sent
            if (msg.id && pendingCommands.has(msg.id)) {
                const pending = pendingCommands.get(msg.id)!;
                pendingCommands.delete(msg.id);
                if (msg.error) {
                    pending.reject(new Error(msg.error.message || 'CDP command failed'));
                } else {
                    pending.resolve(msg.result || {});
                }
            }
        } catch { }
    });

    ws.on('close', () => {
        console.log('[RelayBridge] 🔌 Browser relay extension disconnected.');
        relayClient = null;
        // Reject all pending commands
        for (const [id, pending] of pendingCommands) {
            pending.reject(new Error('Relay disconnected'));
            pendingCommands.delete(id);
        }
    });
}

/**
 * Check if a browser relay extension is currently connected.
 */
export function isRelayConnected(): boolean {
    return relayClient !== null && relayClient.readyState === WebSocket.OPEN;
}

/**
 * Send a CDP command to the relay extension and wait for a response.
 */
export async function sendCommand(method: string, params: Record<string, any> = {}): Promise<any> {
    if (!isRelayConnected()) {
        throw new Error('Browser relay extension is not connected');
    }

    const id = commandId++;
    return new Promise<any>((resolve, reject) => {
        const timeout = setTimeout(() => {
            pendingCommands.delete(id);
            reject(new Error(`CDP command '${method}' timed out after 30s`));
        }, 30000);

        pendingCommands.set(id, {
            resolve: (result) => { clearTimeout(timeout); resolve(result); },
            reject: (err) => { clearTimeout(timeout); reject(err); }
        });

        relayClient!.send(JSON.stringify({ id, method, params }));
    });
}

/**
 * Navigate to a URL in the relay browser and return page content.
 * This is a convenience method that combines multiple CDP commands.
 */
export async function navigateAndRead(url: string): Promise<{ title: string; url: string; content: string }> {
    // Navigate
    await sendCommand('Page.enable');
    await sendCommand('Page.navigate', { url });

    // Wait for page to load
    await new Promise(r => setTimeout(r, 4000));

    // Get page info
    const evalResult = await sendCommand('Runtime.evaluate', {
        expression: `JSON.stringify({
            title: document.title,
            url: window.location.href,
            content: (() => {
                const clone = document.body.cloneNode(true);
                clone.querySelectorAll('script, style, nav, footer, header, noscript, iframe, svg').forEach(el => el.remove());
                let text = clone.innerText || clone.textContent || '';
                text = text.replace(/\\n{3,}/g, '\\n\\n').replace(/[ \\t]+/g, ' ').trim();
                return text.substring(0, 3000);
            })()
        })`,
        returnByValue: true
    });

    try {
        const data = JSON.parse(evalResult.result?.value || '{}');
        return {
            title: data.title || 'Unknown',
            url: data.url || url,
            content: data.content || ''
        };
    } catch {
        return { title: 'Unknown', url, content: 'Failed to read page content from relay browser' };
    }
}

/**
 * Read the current page content from the relay browser without navigating.
 */
export async function readContent(): Promise<{ title: string; url: string; content: string }> {
    const evalResult = await sendCommand('Runtime.evaluate', {
        expression: `JSON.stringify({
            title: document.title,
            url: window.location.href,
            content: (() => {
                const clone = document.body.cloneNode(true);
                clone.querySelectorAll('script, style, nav, footer, header, noscript, iframe, svg').forEach(el => el.remove());
                let text = clone.innerText || clone.textContent || '';
                text = text.replace(/\\n{3,}/g, '\\n\\n').replace(/[ \\t]+/g, ' ').trim();
                return text.substring(0, 3000);
            })()
        })`,
        returnByValue: true
    });

    try {
        const data = JSON.parse(evalResult.result?.value || '{}');
        return {
            title: data.title || 'Unknown',
            url: data.url || '',
            content: data.content || ''
        };
    } catch {
        return { title: 'Unknown', url: '', content: 'Failed to read page content from relay browser' };
    }
}

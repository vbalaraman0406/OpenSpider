/**
 * RelayBridge: Bridge between BrowserTool and the Chrome Browser Relay extension.
 * 
 * RELAY-FIRST ARCHITECTURE:
 * When the relay extension is connected, ALL browser actions go through
 * this bridge to the user's real Chrome browser. Headless Playwright is
 * only used when the relay is NOT connected.
 * 
 * Architecture:
 *   BrowserTool → RelayBridge → WebSocket → Extension → chrome.debugger → Chrome
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

// ─── HIGH-LEVEL BROWSER ACTIONS ──────────────────────────────────────────────

/**
 * Navigate to a URL in the relay browser and return page content.
 */
export async function navigateAndRead(url: string): Promise<{ title: string; url: string; content: string }> {
    await sendCommand('Page.enable');
    await sendCommand('Page.navigate', { url });

    // The Chrome extension now handles page load waiting (via chrome.tabs.onUpdated).
    // This buffer is for any additional JS-rendered content after the load event.
    await new Promise(r => setTimeout(r, 6000));

    return readContent();
}

/**
 * Read the current page content from the relay browser.
 */
export async function readContent(): Promise<{ title: string; url: string; content: string }> {
    const evalResult = await sendCommand('Runtime.evaluate', {
        expression: `JSON.stringify({
            title: document.title,
            url: window.location.href,
            content: (() => {
                const clone = document.body.cloneNode(true);
                // Only remove truly non-content elements — keep nav, header, footer, aside
                // because many dashboards (Yahoo Fantasy, etc.) render user data inside these
                clone.querySelectorAll('script, style, noscript, iframe, svg, [class*="ad-container"], [class*="advertisement"], [class*="sponsored"], [id*="google_ads"]').forEach(el => el.remove());
                let text = clone.innerText || clone.textContent || '';
                text = text.replace(/\\n{3,}/g, '\\n\\n').replace(/[ \\t]+/g, ' ').trim();
                return text.substring(0, 8000);
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

/**
 * Click an element in the relay browser using a CSS selector.
 */
export async function clickElement(selector: string): Promise<string> {
    const evalResult = await sendCommand('Runtime.evaluate', {
        expression: `(() => {
            const el = document.querySelector('${selector.replace(/'/g, "\\'")}');
            if (!el) return JSON.stringify({ success: false, error: 'Element not found: ${selector.replace(/'/g, "\\'")}' });
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            el.click();
            return JSON.stringify({ success: true, tag: el.tagName, text: (el.textContent || '').substring(0, 100) });
        })()`,
        returnByValue: true
    });

    try {
        const data = JSON.parse(evalResult.result?.value || '{}');
        if (!data.success) return `Error: ${data.error}`;
        // Wait for any navigation/page update
        await new Promise(r => setTimeout(r, 1500));
        return `Clicked ${data.tag}: "${data.text}"`;
    } catch {
        return 'Click action completed';
    }
}

/**
 * Type text into an element in the relay browser.
 */
export async function typeText(selector: string, text: string): Promise<string> {
    const escapedText = text.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n');
    const escapedSelector = selector.replace(/'/g, "\\'");

    const evalResult = await sendCommand('Runtime.evaluate', {
        expression: `(() => {
            const el = document.querySelector('${escapedSelector}');
            if (!el) return JSON.stringify({ success: false, error: 'Element not found: ${escapedSelector}' });
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            el.focus();
            el.value = '${escapedText}';
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            return JSON.stringify({ success: true, tag: el.tagName });
        })()`,
        returnByValue: true
    });

    try {
        const data = JSON.parse(evalResult.result?.value || '{}');
        if (!data.success) return `Error: ${data.error}`;
        return `Typed "${text}" into ${data.tag}`;
    } catch {
        return 'Type action completed';
    }
}

/**
 * Scroll the page in the relay browser.
 */
export async function scrollPage(direction: string): Promise<string> {
    const amount = direction === 'up' ? -500 : 500;
    await sendCommand('Runtime.evaluate', {
        expression: `window.scrollBy(0, ${amount})`,
        returnByValue: true
    });
    await new Promise(r => setTimeout(r, 500));
    return `Scrolled ${direction}`;
}

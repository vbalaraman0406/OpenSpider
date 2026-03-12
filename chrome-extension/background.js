// chrome-extension/background.js
let ws = null;
let attachedTabId = null;

// SECURITY: CDP Method Allowlist
// The relay only executes CDP commands in this list.
// This prevents a malicious page from using the debugger bridge to:
//   - Read arbitrary files (Page.captureSnapshot, IO.read)
//   - Access other tabs' data (Target.activateTarget + DOM reads)
//   - Exfiltrate cookies / localStorage from other origins
//   - Execute arbitrary JS in privileged contexts
//   - Control network traffic (Fetch.enable, Network.setCookies)
const ALLOWED_CDP_METHODS = new Set([
    // DOM inspection (read-only)
    'DOM.getDocument',
    'DOM.querySelector',
    'DOM.querySelectorAll',
    'DOM.getOuterHTML',
    'DOM.describeNode',
    'DOM.getAttributes',
    'DOM.getBoxModel',
    'DOM.getContentQuads',
    // Input simulation (needed for click/type)
    'Input.dispatchMouseEvent',
    'Input.dispatchKeyEvent',
    'Input.insertText',
    // Page lifecycle
    'Page.navigate',
    'Page.reload',
    'Page.getLayoutMetrics',
    'Page.captureScreenshot',
    'Page.enable',
    // Runtime JS evaluation (needed for read_content extraction)
    'Runtime.evaluate',
    'Runtime.callFunctionOn',
    'Runtime.getProperties',
    'Runtime.enable',
    // Emulation (viewport, user agent)
    'Emulation.setDeviceMetricsOverride',
    'Emulation.setUserAgentOverride',
    // Network (monitoring only, NOT fetch interception)
    'Network.enable',
    'Network.disable',
    // Target management (for tab info only)
    'Target.getTargetInfo',
]);

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'attach') {
        attachDebugger(request.tabId, request.token, request.port || 4001, request.host || '127.0.0.1');
        sendResponse({ success: true });
    } else if (request.action === 'detach') {
        detachDebugger(request.tabId);
        sendResponse({ success: true });
    } else if (request.action === 'status') {
        sendResponse({ tabId: attachedTabId });
    }
    return true;
});

async function attachDebugger(tabId, token, port, host) {
    if (attachedTabId) {
        await detachDebugger(attachedTabId);
    }

    try {
        await chrome.debugger.attach({ tabId: tabId }, "1.3");
        console.log("Attached to tab", tabId);
        attachedTabId = tabId;
        chrome.action.setBadgeText({ text: "...", tabId: tabId });
        connectWebSocket(tabId, token, port, host);
    } catch (err) {
       console.error("Failed to attach:", err);
       chrome.action.setBadgeText({ text: "ERR", tabId: tabId });
    }
}

async function detachDebugger(tabId) {
    if (!tabId) return;
    try {
        await chrome.debugger.detach({ tabId: tabId });
        console.log("Detached from tab", tabId);
    } catch (e) {
        console.warn("Detach warning", e);
    }
    if (ws) {
        ws.close();
        ws = null;
    }
    attachedTabId = null;
    chrome.action.setBadgeText({ text: "", tabId: tabId });
}

function connectWebSocket(tabId, token, port, host) {
    // Support both local and remote VPS connections
    const wsUrl = `ws://${host}:${port}/?apiKey=${token}`;
    console.log("Connecting to", wsUrl.replace(token, '***'));

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log("WebSocket connected to OpenSpider Relay");
        // Register as a browser relay extension (not just a dashboard client)
        ws.send(JSON.stringify({ type: 'relay_register' }));
        chrome.action.setBadgeText({ text: "ON", tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: "#00AA00", tabId: tabId });
    };

    ws.onmessage = (event) => {
        // Relay CDP commands from Node server -> Chrome Tabs
        try {
            const msg = JSON.parse(event.data);

            // SECURITY: Validate CDP method against allowlist before executing.
            // Reject any method not explicitly permitted to prevent malicious command injection.
            if (msg.id && msg.method) {
                if (!ALLOWED_CDP_METHODS.has(msg.method)) {
                    console.warn(`[OpenSpider Security] Blocked disallowed CDP method: ${msg.method}`);
                    // Send back an error response so the relay doesn't hang
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({
                            id: msg.id,
                            result: {},
                            error: { message: `Method '${msg.method}' is not in the OpenSpider CDP allowlist.` }
                        }));
                    }
                    return;
                }

                chrome.debugger.sendCommand({ tabId: tabId }, msg.method, msg.params, (result) => {
                    const response = {
                        id: msg.id,
                        result: result || {},
                        error: chrome.runtime.lastError ? { message: chrome.runtime.lastError.message } : undefined
                    };
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify(response));
                    }
                });
            }
        } catch (e) {
            console.error("Parse error", e);
        }
    };

    ws.onclose = () => {
        console.log("WebSocket closed");
        chrome.action.setBadgeText({ text: "!", tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: "#FF0000", tabId: tabId });
        detachDebugger(tabId);
    };

    ws.onerror = (err) => {
        console.error("WebSocket error", err);
        chrome.action.setBadgeText({ text: "!", tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: "#FF0000", tabId: tabId });
    };

    // Relay CDP events from Chrome Tabs -> Node server
    chrome.debugger.onEvent.addListener((source, method, params) => {
        if (source.tabId === tabId && ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                method: method,
                params: params
            }));
        }
    });

    // Auto-detach if tab is destroyed
    chrome.debugger.onDetach.addListener((source, reason) => {
        if (source.tabId === tabId) {
            console.log("Debugger detached automatically", reason);
            detachDebugger(tabId);
        }
    });
}

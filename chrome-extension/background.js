// chrome-extension/background.js
let ws = null;
let attachedTabId = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'attach') {
        attachDebugger(request.tabId, request.token, request.port || 18792);
        sendResponse({ success: true });
    } else if (request.action === 'detach') {
        detachDebugger(request.tabId);
        sendResponse({ success: true });
    } else if (request.action === 'status') {
        sendResponse({ tabId: attachedTabId });
    }
    return true;
});

async function attachDebugger(tabId, token, port) {
    if (attachedTabId) {
        await detachDebugger(attachedTabId);
    }

    try {
        await chrome.debugger.attach({ tabId: tabId }, "1.3");
        console.log("Attached to tab", tabId);
        attachedTabId = tabId;
        chrome.action.setBadgeText({ text: "...", tabId: tabId });

        connectWebSocket(tabId, token, port);

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

function connectWebSocket(tabId, token, port) {
    const wsUrl = `ws://127.0.0.1:${port}/?token=${token}`;
    console.log("Connecting to", wsUrl);
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log("WebSocket connected to OpenSpider Relay");
        chrome.action.setBadgeText({ text: "ON", tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: "#00AA00", tabId: tabId });
    };

    ws.onmessage = (event) => {
        // Relay CDP commands from Node server -> Chrome Tabs
        try {
            const msg = JSON.parse(event.data);
            if (msg.id && msg.method) {
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

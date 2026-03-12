// chrome-extension/background.js
let ws = null;
let attachedTabId = null;
let agentTabId = null; // Separate tab created for agent navigation
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 3;

// SECURITY: CDP Method Allowlist
const ALLOWED_CDP_METHODS = new Set([
    'DOM.getDocument',
    'DOM.querySelector',
    'DOM.querySelectorAll',
    'DOM.getOuterHTML',
    'DOM.describeNode',
    'DOM.getAttributes',
    'DOM.getBoxModel',
    'DOM.getContentQuads',
    'Input.dispatchMouseEvent',
    'Input.dispatchKeyEvent',
    'Input.insertText',
    'Page.navigate',
    'Page.reload',
    'Page.getLayoutMetrics',
    'Page.captureScreenshot',
    'Page.enable',
    'Runtime.evaluate',
    'Runtime.callFunctionOn',
    'Runtime.getProperties',
    'Runtime.enable',
    'Emulation.setDeviceMetricsOverride',
    'Emulation.setUserAgentOverride',
    'Network.enable',
    'Network.disable',
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
        sendResponse({ tabId: attachedTabId, agentTabId: agentTabId });
    } else if (request.action === 'exportCookies') {
        // Handle cookie export in background to avoid mixed-content blocking
        handleExportCookies(request).then(sendResponse).catch(err => {
            sendResponse({ success: false, error: err.message });
        });
        return true; // Keep message channel open for async response
    }
    return true;
});

/**
 * Export cookies from the current tab to the OpenSpider server.
 * Runs in the service worker context to avoid mixed-content blocking
 * that occurs when the popup (inheriting HTTPS page context) tries
 * to fetch from HTTP localhost.
 */
async function handleExportCookies({ tabUrl, host, port, token }) {
    console.log(`[CookieExport] Starting export for URL: ${tabUrl} → ${host}:${port}`);

    // 1. Get cookies matching the exact tab URL
    let cookies = await chrome.cookies.getAll({ url: tabUrl });
    console.log(`[CookieExport] Cookies from URL match: ${cookies.length}`);

    // 2. Also get cookies from the root domain (e.g., .yahoo.com)
    //    chrome.cookies.getAll({url}) misses parent-domain cookies
    try {
        const urlObj = new URL(tabUrl);
        const hostParts = urlObj.hostname.split('.');
        // Get root domain: e.g., "sports.yahoo.com" → ".yahoo.com"
        if (hostParts.length >= 2) {
            const rootDomain = '.' + hostParts.slice(-2).join('.');
            const domainCookies = await chrome.cookies.getAll({ domain: rootDomain });
            console.log(`[CookieExport] Cookies from domain '${rootDomain}': ${domainCookies.length}`);

            // Merge and deduplicate by domain+name+path
            const seen = new Set(cookies.map(c => `${c.domain}|${c.name}|${c.path}`));
            for (const dc of domainCookies) {
                const key = `${dc.domain}|${dc.name}|${dc.path}`;
                if (!seen.has(key)) {
                    cookies.push(dc);
                    seen.add(key);
                }
            }
            console.log(`[CookieExport] Total after merge: ${cookies.length}`);
        }
    } catch (e) {
        console.warn(`[CookieExport] Domain broadening failed:`, e.message);
    }

    if (cookies.length === 0) {
        return { success: false, error: 'No cookies found for this site.' };
    }

    // 3. Remap Chrome cookies to Playwright-compatible format
    const playwrightCookies = cookies.map(c => ({
        name: c.name,
        value: c.value,
        domain: c.domain,
        path: c.path,
        secure: c.secure,
        httpOnly: c.httpOnly,
        sameSite: ['unspecified', 'no_restriction'].includes(c.sameSite)
            ? 'None'
            : (c.sameSite === 'lax' ? 'Lax' : 'Strict'),
        expires: c.expirationDate || -1
    }));

    // 4. Send to server — ALWAYS use 127.0.0.1 for cookie export.
    // The extension and server are always on the same machine. The user-specified
    // host (e.g. Tailscale IP) is only needed for the WebSocket relay connection.
    // Chrome's Private Network Access policy blocks fetch() to CGNAT IPs (100.x.x.x)
    // but exempts WebSocket, which is why Attach works but fetch would fail.
    const cookieHost = '127.0.0.1';

    let response = null;
    let lastError = null;

    try {
        const url = `http://${cookieHost}:${port}/api/v1/browser/cookies`;
        console.log(`[CookieExport] Sending to ${url}...`);
        response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': token
            },
            body: JSON.stringify({ cookies: playwrightCookies })
        });
        console.log(`[CookieExport] Response: ${response.status}`);
    } catch (e) {
        lastError = e;
        console.warn(`[CookieExport] fetch failed:`, e.message);
    }

    if (!response) {
        return { success: false, error: `Cannot reach server at ${host}:${port}. ${lastError?.message || 'Check host, port, and firewall.'}` };
    }

    if (!response.ok) {
        const errorText = await response.text().catch(() => '');
        return { success: false, error: `Server returned ${response.status}: ${errorText}` };
    }

    const data = await response.json();
    console.log(`[CookieExport] ✅ Success: ${data.count} cookies exported, ${data.persisted} total`);
    return { success: true, count: data.count, persisted: data.persisted };
}

async function attachDebugger(tabId, token, port, host) {
    if (attachedTabId) {
        await detachDebugger(attachedTabId);
    }

    try {
        await chrome.debugger.attach({ tabId: tabId }, "1.3");
        console.log("Attached to tab", tabId);
        attachedTabId = tabId;
        reconnectAttempts = 0;
        chrome.action.setBadgeText({ text: "..." });
        connectWebSocket(tabId, token, port, host);
    } catch (err) {
       console.error("Failed to attach:", err);
       chrome.action.setBadgeText({ text: "ERR" });
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
    agentTabId = null;
    reconnectAttempts = 0;
    chrome.action.setBadgeText({ text: "" });
}

// Store connection params for reconnection
let lastToken = null;
let lastPort = null;
let lastHost = null;

function connectWebSocket(tabId, token, port, host) {
    lastToken = token;
    lastPort = port;
    lastHost = host;

    const wsUrl = `ws://${host}:${port}/?apiKey=${token}`;
    console.log("Connecting to", wsUrl.replace(token, '***'));

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log("WebSocket connected to OpenSpider Relay");
        ws.send(JSON.stringify({ type: 'relay_register' }));
        chrome.action.setBadgeText({ text: "ON" });
        chrome.action.setBadgeBackgroundColor({ color: "#00AA00" });
    };

    ws.onmessage = async (event) => {
        try {
            const msg = JSON.parse(event.data);

            if (msg.id && msg.method) {
                if (!ALLOWED_CDP_METHODS.has(msg.method)) {
                    console.warn(`[Security] Blocked CDP method: ${msg.method}`);
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({
                            id: msg.id,
                            result: {},
                            error: { message: `Method '${msg.method}' is not allowed.` }
                        }));
                    }
                    return;
                }

                // NEW-TAB NAVIGATION: When agent navigates, create a new tab
                // so the user's original tab stays untouched
                if (msg.method === 'Page.navigate' && msg.params && msg.params.url) {
                    await handleNavigation(msg);
                    return;
                }

                // Use the active agent tab (or fallback to attached tab)
                const targetTabId = agentTabId || attachedTabId;
                if (!targetTabId) {
                    sendError(msg.id, 'No tab attached');
                    return;
                }

                chrome.debugger.sendCommand({ tabId: targetTabId }, msg.method, msg.params, (result) => {
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
        ws = null;

        // AUTO-RECONNECT: Try to reconnect every 5s (up to 60 attempts = 5 min)
        // The debugger stays attached — only the WebSocket needs to reconnect
        if (attachedTabId && lastToken && lastPort && lastHost) {
            chrome.action.setBadgeText({ text: "RE" });
            chrome.action.setBadgeBackgroundColor({ color: "#FFAA00" });
            scheduleWsReconnect();
        } else {
            chrome.action.setBadgeText({ text: "!" });
            chrome.action.setBadgeBackgroundColor({ color: "#FF0000" });
        }
    };

    ws.onerror = (err) => {
        console.error("WebSocket error", err);
        // Don't update badge here — onclose will fire right after
    };

    // Relay CDP events from Chrome -> server
    chrome.debugger.onEvent.addListener((source, method, params) => {
        const targetTab = agentTabId || attachedTabId;
        if (source.tabId === targetTab && ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ method, params }));
        }
    });

    // AUTO-RECONNECT on detach instead of killing everything
    chrome.debugger.onDetach.addListener((source, reason) => {
        const targetTab = agentTabId || attachedTabId;
        if (source.tabId === targetTab) {
            console.log("Debugger detached:", reason);

            // If user manually cancelled, fully disconnect
            if (reason === 'canceled_by_user') {
                console.log("User cancelled debugging. Fully disconnecting.");
                attachedTabId = null;
                agentTabId = null;
                if (ws) { ws.close(); ws = null; }
                chrome.action.setBadgeText({ text: "" });
                return;
            }

            // Otherwise, try to re-attach (cross-domain nav, target crashed, etc.)
            if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                reconnectAttempts++;
                console.log(`Auto-reconnect attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}...`);
                chrome.action.setBadgeText({ text: "RE" });
                chrome.action.setBadgeBackgroundColor({ color: "#FFAA00" });

                setTimeout(async () => {
                    const tabToReattach = agentTabId || attachedTabId;
                    if (!tabToReattach) return;
                    try {
                        await chrome.debugger.attach({ tabId: tabToReattach }, "1.3");
                        console.log("Re-attached successfully to tab", tabToReattach);
                        chrome.action.setBadgeText({ text: "ON" });
                        chrome.action.setBadgeBackgroundColor({ color: "#00AA00" });
                        reconnectAttempts = 0;
                    } catch (err) {
                        console.warn("Re-attach failed:", err);
                        if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                            console.error("Max reconnect attempts reached. Disconnecting.");
                            attachedTabId = null;
                            agentTabId = null;
                            chrome.action.setBadgeText({ text: "!" });
                        }
                    }
                }, 2000);
            }
        }
    });
}

/**
 * Handle Page.navigate by creating a new tab for the agent.
 * This keeps the user's original tab untouched.
 */
async function handleNavigation(msg) {
    const url = msg.params.url;
    console.log("[Relay] Agent navigating to:", url);

    try {
        // If we already have an agent tab, reuse it
        if (agentTabId) {
            try {
                // Verify the agent tab still exists
                await chrome.tabs.get(agentTabId);
                // Detach debugger from old tab, navigate, re-attach
                try { await chrome.debugger.detach({ tabId: agentTabId }); } catch {}
                await chrome.tabs.update(agentTabId, { url: url, active: true });
                // Wait for tab to start loading
                await new Promise(r => setTimeout(r, 1000));
                await chrome.debugger.attach({ tabId: agentTabId }, "1.3");
                reconnectAttempts = 0;

                // Wait for page to load
                await waitForPageLoad(agentTabId);

                sendSuccess(msg.id, { frameId: 'agent-tab' });
                return;
            } catch (e) {
                console.warn("Agent tab no longer exists, creating new one");
                agentTabId = null;
            }
        }

        // Create a new tab for the agent
        const newTab = await chrome.tabs.create({ url: url, active: true });
        agentTabId = newTab.id;
        console.log("[Relay] Created agent tab:", agentTabId);

        // Detach debugger from the original tab
        if (attachedTabId && attachedTabId !== agentTabId) {
            try { await chrome.debugger.detach({ tabId: attachedTabId }); } catch {}
        }

        // Wait for tab to start loading, then attach debugger
        await new Promise(r => setTimeout(r, 1500));
        await chrome.debugger.attach({ tabId: agentTabId }, "1.3");
        reconnectAttempts = 0;

        // Wait for page to fully load
        await waitForPageLoad(agentTabId);

        sendSuccess(msg.id, { frameId: 'agent-tab' });
    } catch (err) {
        console.error("Navigation error:", err);
        sendError(msg.id, err.message || 'Navigation failed');
    }
}

/**
 * Wait for a tab to finish loading (with timeout).
 */
function waitForPageLoad(tabId) {
    return new Promise((resolve) => {
        const timeout = setTimeout(() => {
            chrome.tabs.onUpdated.removeListener(listener);
            resolve(); // Timeout after 10s — continue anyway
        }, 10000);

        function listener(updatedTabId, changeInfo) {
            if (updatedTabId === tabId && changeInfo.status === 'complete') {
                clearTimeout(timeout);
                chrome.tabs.onUpdated.removeListener(listener);
                // Extra delay for JS-heavy pages
                setTimeout(resolve, 1000);
            }
        }
        chrome.tabs.onUpdated.addListener(listener);
    });
}

function sendSuccess(id, result) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ id, result: result || {} }));
    }
}

function sendError(id, message) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ id, result: {}, error: { message } }));
    }
}

/**
 * Auto-reconnect WebSocket to the OpenSpider server.
 * Retries every 5s for up to 5 minutes (60 attempts).
 * The debugger stays attached to the tab during reconnection.
 */
let wsReconnectTimer = null;
let wsReconnectCount = 0;
const MAX_WS_RECONNECTS = 60;

function scheduleWsReconnect() {
    if (wsReconnectTimer) return; // Already scheduled
    wsReconnectCount = 0;
    attemptWsReconnect();
}

function attemptWsReconnect() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        // Already connected
        wsReconnectTimer = null;
        wsReconnectCount = 0;
        return;
    }

    if (wsReconnectCount >= MAX_WS_RECONNECTS) {
        console.error("[Relay] Max WebSocket reconnect attempts reached. Giving up.");
        chrome.action.setBadgeText({ text: "!" });
        chrome.action.setBadgeBackgroundColor({ color: "#FF0000" });
        wsReconnectTimer = null;
        return;
    }

    if (!lastToken || !lastPort || !lastHost) {
        wsReconnectTimer = null;
        return;
    }

    wsReconnectCount++;
    console.log(`[Relay] WebSocket reconnect attempt ${wsReconnectCount}/${MAX_WS_RECONNECTS}...`);

    const wsUrl = `ws://${lastHost}:${lastPort}/?apiKey=${lastToken}`;
    const reconnectWs = new WebSocket(wsUrl);

    reconnectWs.onopen = () => {
        console.log("[Relay] WebSocket reconnected successfully!");
        ws = reconnectWs;
        wsReconnectTimer = null;
        wsReconnectCount = 0;

        // Re-register as relay
        ws.send(JSON.stringify({ type: 'relay_register' }));
        chrome.action.setBadgeText({ text: "ON" });
        chrome.action.setBadgeBackgroundColor({ color: "#00AA00" });

        // Re-attach message handler
        ws.onmessage = async (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.id && msg.method) {
                    if (!ALLOWED_CDP_METHODS.has(msg.method)) {
                        sendError(msg.id, `Method '${msg.method}' is not allowed.`);
                        return;
                    }
                    if (msg.method === 'Page.navigate' && msg.params && msg.params.url) {
                        await handleNavigation(msg);
                        return;
                    }
                    const targetTabId = agentTabId || attachedTabId;
                    if (!targetTabId) { sendError(msg.id, 'No tab attached'); return; }
                    chrome.debugger.sendCommand({ tabId: targetTabId }, msg.method, msg.params, (result) => {
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
            } catch (e) { console.error("Parse error", e); }
        };

        // Re-attach close handler for future disconnects
        ws.onclose = () => {
            console.log("WebSocket closed (reconnected session)");
            ws = null;
            if (attachedTabId && lastToken) {
                chrome.action.setBadgeText({ text: "RE" });
                chrome.action.setBadgeBackgroundColor({ color: "#FFAA00" });
                scheduleWsReconnect();
            }
        };
    };

    reconnectWs.onerror = () => {
        // Will trigger onclose
    };

    reconnectWs.onclose = () => {
        // Retry in 5 seconds
        wsReconnectTimer = setTimeout(() => {
            wsReconnectTimer = null;
            attemptWsReconnect();
        }, 5000);
    };
}

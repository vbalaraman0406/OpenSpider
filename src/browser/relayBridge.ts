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

// ─── Human-like Mouse Movement State ─────────────────────────────────────────
// Track last known mouse position for continuous Bézier paths between clicks
let lastMouseX: number | null = null;
let lastMouseY: number | null = null;

/**
 * Generate a cubic Bézier curve path between two points with human-like
 * randomization. Mimics ghost-cursor / Google Antigravity IDE style movements.
 * 
 * - Random control points create natural curved paths (not straight lines)
 * - Per-point noise simulates hand tremor (±1.5px)
 * - Variable number of points (15-25) for natural density
 */
function generateBezierPath(
    startX: number, startY: number,
    endX: number, endY: number
): Array<{ x: number; y: number }> {
    const distance = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));
    const numPoints = Math.min(30, Math.max(15, Math.floor(distance / 20) + Math.floor(Math.random() * 8)));

    // Random control points — offset perpendicular to the straight line
    // This creates a natural curve, not a straight-line movement
    const midX = (startX + endX) / 2;
    const midY = (startY + endY) / 2;
    const perpX = -(endY - startY); // Perpendicular vector
    const perpY = (endX - startX);
    const perpLen = Math.sqrt(perpX * perpX + perpY * perpY) || 1;

    // Control point 1: ±30-50% offset from midpoint along perpendicular
    const spread1 = (0.3 + Math.random() * 0.2) * (Math.random() > 0.5 ? 1 : -1);
    const cp1x = midX + perpX / perpLen * distance * spread1 * 0.3 + (Math.random() - 0.5) * 30;
    const cp1y = midY + perpY / perpLen * distance * spread1 * 0.3 + (Math.random() - 0.5) * 30;

    // Control point 2: slight overshoot bias toward the target
    const spread2 = (0.1 + Math.random() * 0.15) * (Math.random() > 0.5 ? 1 : -1);
    const cp2x = endX + (endX - startX) * 0.05 + perpX / perpLen * distance * spread2 * 0.2;
    const cp2y = endY + (endY - startY) * 0.05 + perpY / perpLen * distance * spread2 * 0.2;

    const points: Array<{ x: number; y: number }> = [];
    for (let i = 0; i <= numPoints; i++) {
        const t = i / numPoints;
        const u = 1 - t;

        // Cubic Bézier formula: B(t) = (1-t)³P₀ + 3(1-t)²tP₁ + 3(1-t)t²P₂ + t³P₃
        const x = u * u * u * startX
                + 3 * u * u * t * cp1x
                + 3 * u * t * t * cp2x
                + t * t * t * endX;
        const y = u * u * u * startY
                + 3 * u * u * t * cp1y
                + 3 * u * t * t * cp2y
                + t * t * t * endY;

        // Add micro-jitter to simulate hand tremor (±1.5px, decreasing near target)
        const noise = (1 - t) * 1.5;
        points.push({
            x: x + (Math.random() - 0.5) * noise * 2,
            y: y + (Math.random() - 0.5) * noise * 2
        });
    }

    return points;
}

// ─── Visual Ghost Cursor Overlay ─────────────────────────────────────────────
// CDP Input.dispatchMouseEvent doesn't move the OS cursor visually.
// Injects a cursor + animation engine, then batch-sends Bézier paths
// in ONE Runtime.evaluate. Animation runs entirely client-side.

let ghostCursorInjected = false;

/**
 * Inject the ghost cursor system. Creates: SVG cursor, canvas trail,
 * animation engine, click effects, and hides the native OS cursor.
 */
async function injectGhostCursor(): Promise<void> {
    try {
        const js = [
            '(function(){',
            'if(document.getElementById("__os_cursor"))return"exists";',
            // Hide native cursor
            'var s=document.createElement("style");s.id="__os_hide";',
            's.textContent="*{cursor:none!important}";document.head.appendChild(s);',
            // Trail canvas
            'var t=document.createElement("canvas");t.id="__os_trail";',
            't.width=window.innerWidth;t.height=window.innerHeight;',
            'Object.assign(t.style,{position:"fixed",top:"0",left:"0",',
            'width:"100vw",height:"100vh",pointerEvents:"none",zIndex:"2147483645",opacity:"0.5"});',
            'document.documentElement.appendChild(t);',
            // SVG cursor
            'var c=document.createElement("div");c.id="__os_cursor";',
            'c.innerHTML=\'<svg width="20" height="24" viewBox="0 0 20 24"><path d="M4 1L4 19L7.5 15.5L11 21.5L13.5 20.5L10 14L15.5 13.5L4 1Z" fill="rgba(255,50,50,0.95)" stroke="white" stroke-width="1.2"/></svg>\';',
            'Object.assign(c.style,{position:"fixed",left:"-50px",top:"-50px",',
            'pointerEvents:"none",zIndex:"2147483646",',
            'filter:"drop-shadow(0 2px 6px rgba(0,0,0,0.4))",willChange:"left,top"});',
            'document.documentElement.appendChild(c);',
            // Click style
            'var rs=document.createElement("style");rs.id="__os_rstyle";',
            'rs.textContent="@keyframes __osr{0%{transform:scale(0.3);opacity:1}100%{transform:scale(2.5);opacity:0}}@keyframes __osrr{0%{transform:scale(0.5);opacity:0.8}100%{transform:scale(3);opacity:0}}";',
            'document.head.appendChild(rs);',
            // Resize
            'window.addEventListener("resize",function(){t.width=innerWidth;t.height=innerHeight});',
            // Animation engine
            'window.__os_anim=function(pts,dly,cb){var cur=document.getElementById("__os_cursor"),',
            'tr=document.getElementById("__os_trail"),ctx=tr?tr.getContext("2d"):null,tp=[],i=0;',
            'function go(){if(i>=pts.length){if(cb)cb();return}',
            'var p=pts[i];if(cur){cur.style.left=p.x+"px";cur.style.top=p.y+"px"}',
            'if(ctx){tp.push({x:p.x+4,y:p.y+4});if(tp.length>50)tp.shift();',
            'ctx.clearRect(0,0,ctx.canvas.width,ctx.canvas.height);',
            'for(var j=0;j<tp.length;j++){var a=j/tp.length;ctx.beginPath();',
            'ctx.arc(tp[j].x,tp[j].y,1.5+a*2.5,0,Math.PI*2);',
            'ctx.fillStyle="rgba(255,50,50,"+(a*0.6)+")";ctx.fill()}}',
            'i++;setTimeout(go,dly[i-1]||15)}go()};',
            // Click effect
            'window.__os_click=function(x,y){',
            'var d=document.createElement("div");',
            'Object.assign(d.style,{position:"fixed",left:(x-6)+"px",top:(y-6)+"px",',
            'width:"12px",height:"12px",borderRadius:"50%",',
            'background:"rgba(255,50,50,0.9)",pointerEvents:"none",',
            'zIndex:"2147483647",animation:"__osr 0.4s ease-out forwards"});',
            'document.documentElement.appendChild(d);',
            'var r=document.createElement("div");',
            'Object.assign(r.style,{position:"fixed",left:(x-15)+"px",top:(y-15)+"px",',
            'width:"30px",height:"30px",borderRadius:"50%",',
            'border:"2px solid rgba(255,50,50,0.6)",pointerEvents:"none",',
            'zIndex:"2147483647",animation:"__osrr 0.5s ease-out forwards"});',
            'document.documentElement.appendChild(r);',
            'setTimeout(function(){d.remove();r.remove()},600)};',
            'return"injected"})()'
        ].join('\n');
        await sendCommand('Runtime.evaluate', { expression: js, returnByValue: true });
        ghostCursorInjected = true;
        console.log('[RelayBridge] \uD83D\uDC46 Ghost cursor injected (client-side animation engine)');
    } catch (e: any) {
        console.warn('[RelayBridge] Ghost cursor injection failed:', e.message);
    }
}

/**
 * Animate the ghost cursor along a B\u00e9zier path entirely client-side.
 * Sends all points + timing in ONE Runtime.evaluate call.
 * Then waits server-side for the animation to complete before returning.
 */
async function animateGhostCursor(points: Array<{ x: number; y: number }>): Promise<void> {
    if (!ghostCursorInjected || points.length === 0) return;
    const delays: number[] = [];
    for (let i = 0; i < points.length; i++) {
        const progress = i / points.length;
        const speedFactor = 1 - 4 * Math.pow(progress - 0.5, 2);
        delays.push(Math.floor(10 + (1 - speedFactor) * 20 + Math.random() * 5));
    }
    const totalMs = delays.reduce((a, b) => a + b, 0);
    const pj = JSON.stringify(points.map(p => ({ x: Math.round(p.x), y: Math.round(p.y) })));
    const dj = JSON.stringify(delays);
    try {
        await sendCommand('Runtime.evaluate', {
            expression: `window.__os_anim && window.__os_anim(${pj}, ${dj})`,
            returnByValue: true
        });
        await new Promise(r => setTimeout(r, totalMs + 50));
    } catch { }
}

/**
 * Show a click effect at the given position.
 */
async function showClickEffect(x: number, y: number): Promise<void> {
    if (!ghostCursorInjected) return;
    try {
        await sendCommand('Runtime.evaluate', {
            expression: `window.__os_click && window.__os_click(${Math.round(x)}, ${Math.round(y)})`,
            returnByValue: true
        });
    } catch { }
}


// Reconnection event callbacks
const reconnectCallbacks: Array<() => void> = [];

/**
 * Wait for the relay to reconnect within a timeout window.
 * Returns true if relay reconnected, false if timed out.
 */
export function waitForRelay(maxMs = 15000, pollMs = 2000): Promise<boolean> {
    if (isRelayConnected()) return Promise.resolve(true);

    return new Promise<boolean>((resolve) => {
        const start = Date.now();
        console.log(`[RelayBridge] ⏳ Waiting up to ${maxMs / 1000}s for relay to reconnect...`);

        // Fast path: listen for reconnect event
        const onReconnect = () => {
            clearInterval(poll);
            clearTimeout(timeout);
            console.log(`[RelayBridge] ✅ Relay reconnected after ${Date.now() - start}ms`);
            resolve(true);
        };
        reconnectCallbacks.push(onReconnect);

        // Polling fallback
        const poll = setInterval(() => {
            if (isRelayConnected()) {
                clearInterval(poll);
                clearTimeout(timeout);
                const idx = reconnectCallbacks.indexOf(onReconnect);
                if (idx >= 0) reconnectCallbacks.splice(idx, 1);
                console.log(`[RelayBridge] ✅ Relay reconnected after ${Date.now() - start}ms`);
                resolve(true);
            }
        }, pollMs);

        // Hard timeout
        const timeout = setTimeout(() => {
            clearInterval(poll);
            const idx = reconnectCallbacks.indexOf(onReconnect);
            if (idx >= 0) reconnectCallbacks.splice(idx, 1);
            console.log(`[RelayBridge] ⏰ Relay did not reconnect within ${maxMs / 1000}s — falling back to headless`);
            resolve(false);
        }, maxMs);
    });
}

/**
 * Register a WebSocket client as the browser relay extension.
 */
export function registerRelay(ws: WebSocket): void {
    relayClient = ws;
    console.log('[RelayBridge] 🔗 Browser relay extension connected.');

    // Fire any pending reconnect waiters
    while (reconnectCallbacks.length > 0) {
        const cb = reconnectCallbacks.shift();
        if (cb) cb();
    }

    // ─── HEARTBEAT: Ping every 25s to prevent TCP idle timeout ───
    // Without this, the OS kills the connection after ~2min of inactivity
    // and neither side knows until the next message attempt.
    const pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.ping();
        } else {
            clearInterval(pingInterval);
        }
    }, 25000);

    ws.on('pong', () => {
        // Extension is alive — connection is healthy
    });

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
        clearInterval(pingInterval);
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

// ─── SMART WAIT UTILITIES ────────────────────────────────────────────────────

/**
 * Poll the browser until document.readyState === 'complete', then wait
 * an extra buffer for SPA hydration. Much smarter than a fixed delay.
 * 
 * @param maxWaitMs   Hard timeout (default 12s)
 * @param hydrationMs Extra wait after readyState complete (default 1500ms)
 * @param pollMs      Polling interval (default 500ms)
 */
async function waitForPageReady(maxWaitMs = 12000, hydrationMs = 1500, pollMs = 500): Promise<void> {
    const start = Date.now();
    while (Date.now() - start < maxWaitMs) {
        try {
            const result = await sendCommand('Runtime.evaluate', {
                expression: `document.readyState`,
                returnByValue: true
            });
            if (result.result?.value === 'complete') {
                // Page is loaded — wait a bit more for SPA JS hydration
                await new Promise(r => setTimeout(r, hydrationMs));
                return;
            }
        } catch {
            // Eval can fail during navigation — just retry
        }
        await new Promise(r => setTimeout(r, pollMs));
    }
    // Hard timeout reached — proceed anyway
    console.warn('[RelayBridge] waitForPageReady hard timeout reached');
}

/**
 * Post-click smart wait: detect URL change (navigation) vs in-page SPA update.
 * 
 * @param previousUrl  URL before the click
 */
async function waitAfterClick(previousUrl: string): Promise<void> {
    // Short initial settle
    await new Promise(r => setTimeout(r, 400));

    try {
        const result = await sendCommand('Runtime.evaluate', {
            expression: `window.location.href`,
            returnByValue: true
        });
        const currentUrl = result.result?.value || '';

        if (currentUrl !== previousUrl) {
            // URL changed — full navigation happened. Wait for page ready.
            console.log(`[RelayBridge] Post-click navigation detected: ${previousUrl} → ${currentUrl}`);
            await waitForPageReady(8000, 1000);
            // Ghost cursor was destroyed by page navigation — reset and re-inject
            ghostCursorInjected = false;
            await injectGhostCursor();
        } else {
            // Same URL — likely an SPA in-page update. Wait for DOM mutations.
            await new Promise(r => setTimeout(r, 1500));
        }
    } catch {
        // If we can't read URL (page crashed/navigated), just wait
        await new Promise(r => setTimeout(r, 3000));
    }
}

// ─── HIGH-LEVEL BROWSER ACTIONS ──────────────────────────────────────────────

// ─── Cloudflare Challenge Detection & Solving (CDP-based) ──────────────────

interface ChallengeResult {
    blocked: boolean;
    type?: 'js_challenge' | 'turnstile' | 'checkbox' | 'unknown';
    reason: string;
}

/**
 * Detect if the current page is a Cloudflare challenge page.
 */
async function detectCloudflareChallenge(): Promise<ChallengeResult> {
    try {
        const result = await sendCommand('Runtime.evaluate', {
            expression: `(() => {
                const body = (document.body?.innerText || '').toLowerCase();
                const title = (document.title || '').toLowerCase();
                
                // Cloudflare JS challenge ("Just a moment...")
                if ((body.includes('just a moment') && body.includes('checking')) ||
                    title.includes('just a moment') ||
                    (body.includes('verify you are human') && body.length < 2000) ||
                    (body.includes('ray id') && body.includes('cloudflare') && body.length < 3000)) {
                    
                    // Check for Turnstile iframe
                    const iframes = document.querySelectorAll('iframe');
                    for (const iframe of iframes) {
                        const src = (iframe.src || '').toLowerCase();
                        if (src.includes('challenges.cloudflare.com') || src.includes('turnstile')) {
                            return JSON.stringify({ blocked: true, type: 'turnstile', reason: 'Cloudflare Turnstile checkbox' });
                        }
                    }
                    
                    // Check for cf-turnstile container
                    const checkbox = document.querySelector('.cf-turnstile, [data-sitekey], #challenge-form');
                    if (checkbox) {
                        return JSON.stringify({ blocked: true, type: 'turnstile', reason: 'Cloudflare Turnstile widget' });
                    }
                    
                    return JSON.stringify({ blocked: true, type: 'js_challenge', reason: 'Cloudflare JS challenge' });
                }
                
                // Challenge spinner
                if (document.querySelector('#challenge-running, #challenge-spinner, .cf-challenge-page')) {
                    return JSON.stringify({ blocked: true, type: 'js_challenge', reason: 'Cloudflare challenge spinner' });
                }
                
                // Access denied
                if ((title.includes('access denied') || title.includes('attention required')) && body.length < 2000) {
                    return JSON.stringify({ blocked: true, type: 'unknown', reason: 'Cloudflare access denied' });
                }

                return JSON.stringify({ blocked: false, reason: '' });
            })()`,
            returnByValue: true
        });
        return JSON.parse(result.result?.value || '{"blocked":false,"reason":""}');
    } catch {
        return { blocked: false, reason: '' };
    }
}

/**
 * Click the Cloudflare Turnstile checkbox using CDP + Bézier mouse movement.
 */
async function solveCloudflareCheckbox(): Promise<boolean> {
    try {
        // Find the Turnstile iframe bounding box
        const findResult = await sendCommand('Runtime.evaluate', {
            expression: `(() => {
                const iframes = document.querySelectorAll('iframe');
                for (const iframe of iframes) {
                    const src = (iframe.src || '').toLowerCase();
                    if (src.includes('challenges.cloudflare.com') || src.includes('turnstile')) {
                        const rect = iframe.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            return JSON.stringify({ found: true, x: rect.x, y: rect.y, w: rect.width, h: rect.height });
                        }
                    }
                }
                // Search for cf-turnstile container
                const ct = document.querySelector('.cf-turnstile, [data-sitekey]');
                if (ct) {
                    const r = ct.getBoundingClientRect();
                    if (r.width > 0) return JSON.stringify({ found: true, x: r.x, y: r.y, w: r.width, h: r.height });
                }
                return JSON.stringify({ found: false });
            })()`,
            returnByValue: true
        });

        const data = JSON.parse(findResult.result?.value || '{"found":false}');
        if (!data.found) {
            console.log('  [RelayBridge] No Turnstile iframe found');
            return false;
        }

        // Turnstile checkbox is ~30px from left, vertically centered in iframe
        const checkboxX = data.x + Math.min(35, data.w * 0.12);
        const checkboxY = data.y + data.h / 2;

        console.log(`  [RelayBridge] Turnstile at (${Math.round(data.x)}, ${Math.round(data.y)}) ${Math.round(data.w)}x${Math.round(data.h)}, clicking (${Math.round(checkboxX)}, ${Math.round(checkboxY)})`);

        // Bézier mouse path to checkbox
        const startX = lastMouseX ?? (Math.random() * 300 + 200);
        const startY = lastMouseY ?? (Math.random() * 200 + 100);
        const points = generateBezierPath(startX, startY, checkboxX, checkboxY);

        // Fire visual animation client-side
        animateGhostCursor(points);

        for (let i = 0; i < points.length; i++) {
            const p = points[i]!;
            await sendCommand('Input.dispatchMouseEvent', {
                type: 'mouseMoved', x: Math.round(p.x), y: Math.round(p.y), button: 'none'
            });
            const progress = i / points.length;
            const speedFactor = 1 - 4 * Math.pow(progress - 0.5, 2);
            await new Promise(r => setTimeout(r, Math.floor(8 + (1 - speedFactor) * 17 + Math.random() * 5)));
        }

        // Extra hover pause for Turnstile (they monitor hover duration)
        await new Promise(r => setTimeout(r, 200 + Math.floor(Math.random() * 400)));

        // Click with jitter
        const jX = checkboxX + (Math.random() * 4 - 2);
        const jY = checkboxY + (Math.random() * 4 - 2);

        await sendCommand('Input.dispatchMouseEvent', {
            type: 'mousePressed', x: Math.round(jX), y: Math.round(jY), button: 'left', clickCount: 1
        });
        await new Promise(r => setTimeout(r, 60 + Math.floor(Math.random() * 100)));
        await sendCommand('Input.dispatchMouseEvent', {
            type: 'mouseReleased', x: Math.round(jX), y: Math.round(jY), button: 'left', clickCount: 1
        });

        await showClickEffect(jX, jY);

        lastMouseX = checkboxX;
        lastMouseY = checkboxY;

        console.log(`  🖱️ [RelayBridge] Bézier-clicked Turnstile checkbox`);
        return true;
    } catch (err: any) {
        console.error(`  [RelayBridge] Turnstile solve error: ${err.message}`);
        return false;
    }
}


/**
 * Navigate to a URL in the relay browser and return page content.
 * After loading, detects Cloudflare challenges and auto-solves them.
 */
export async function navigateAndRead(url: string): Promise<{ title: string; url: string; content: string }> {
    await sendCommand('Page.enable');
    await sendCommand('Page.navigate', { url });

    // Smart wait: poll for document.readyState instead of fixed 8s delay
    await waitForPageReady();

    // Inject visual ghost cursor on the new page
    ghostCursorInjected = false;
    await injectGhostCursor();

    // ─── Cloudflare / CAPTCHA Detection & Auto-Solve ────────────────
    const MAX_CAPTCHA_ATTEMPTS = 3;
    for (let attempt = 1; attempt <= MAX_CAPTCHA_ATTEMPTS; attempt++) {
        const challenge = await detectCloudflareChallenge();
        if (!challenge.blocked) break;

        console.log(`\n🧩 [RelayBridge] Cloudflare challenge detected: "${challenge.reason}" (attempt ${attempt}/${MAX_CAPTCHA_ATTEMPTS})`);

        if (challenge.type === 'js_challenge') {
            // JS challenge auto-solves — just wait longer
            console.log('  [RelayBridge] Cloudflare JS challenge — waiting for auto-solve...');
            await new Promise(r => setTimeout(r, 6000 + Math.floor(Math.random() * 4000)));
            await waitForPageReady(8000);
            continue;
        }

        if (challenge.type === 'turnstile' || challenge.type === 'checkbox') {
            const solved = await solveCloudflareCheckbox();
            if (solved) {
                console.log('  ✅ [RelayBridge] Cloudflare Turnstile checkbox clicked!');
                // Wait for challenge to process and page to load
                await new Promise(r => setTimeout(r, 3000 + Math.floor(Math.random() * 3000)));
                await waitForPageReady(10000, 2000);
                continue; // Check again in case there's another challenge
            } else {
                console.log('  ⚠️ [RelayBridge] Could not click Turnstile checkbox');
            }
        }

        // Brief pause between attempts
        await new Promise(r => setTimeout(r, 2000 + Math.floor(Math.random() * 2000)));
    }

    return readContent();
}

/**
 * Read the current page content from the relay browser.
 * Optionally accepts a CSS selector to extract only a specific section.
 * Uses smart content prioritization: tables/data first, nav chrome last.
 */
export async function readContent(selector?: string): Promise<{ title: string; url: string; content: string }> {
    const escapedSelector = selector ? selector.replace(/'/g, "\\'") : '';
    
    const evalResult = await sendCommand('Runtime.evaluate', {
        expression: `JSON.stringify({
            title: document.title,
            url: window.location.href,
            content: (() => {
                // If a selector is provided, extract only that section
                const targetSelector = '${escapedSelector}';
                let root;
                if (targetSelector) {
                    root = document.querySelector(targetSelector);
                    if (!root) {
                        // Try common alternatives
                        root = document.querySelector('main') || document.querySelector('[role="main"]') || document.querySelector('#content') || document.querySelector('.content');
                    }
                }
                if (!root) root = document.body;
                
                const clone = root.cloneNode(true);
                // Remove non-content elements
                clone.querySelectorAll('script, style, noscript, iframe, svg, [class*="ad-container"], [class*="advertisement"], [class*="sponsored"], [id*="google_ads"]').forEach(el => el.remove());
                
                // SMART CONTENT PRIORITIZATION:
                // Extract data-rich content first (tables, lists), then general text.
                // This ensures truncation cuts navigation chrome, not user data.
                const parts = [];
                
                // Priority 1: Tables (most data-dense content)
                clone.querySelectorAll('table').forEach(table => {
                    const rows = [];
                    table.querySelectorAll('tr').forEach(tr => {
                        const cells = [];
                        tr.querySelectorAll('th, td').forEach(cell => {
                            cells.push((cell.textContent || '').trim().replace(/\\s+/g, ' '));
                        });
                        if (cells.length > 0) rows.push(cells.join(' | '));
                    });
                    if (rows.length > 0) {
                        parts.push('[TABLE]\\n' + rows.join('\\n'));
                        table.remove(); // Don't double-count
                    }
                });
                
                // Priority 2: Main content area
                const mainEls = clone.querySelectorAll('main, [role="main"], article, .content, #content');
                mainEls.forEach(el => {
                    const text = (el.innerText || el.textContent || '').trim();
                    if (text.length > 50) {
                        parts.push(text);
                        el.remove(); // Don't double-count
                    }
                });
                
                // Priority 3: Everything else (nav, header, footer — lowest priority)
                const remaining = (clone.innerText || clone.textContent || '').trim();
                if (remaining.length > 20) parts.push(remaining);
                
                let text = parts.join('\\n\\n');
                text = text.replace(/\\n{3,}/g, '\\n\\n').replace(/[ \\t]+/g, ' ').trim();
                return text.substring(0, 10000);
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
 * List all visible clickable elements on the current page.
 * Returns a structured text list the agent can use to pick click targets.
 */
export async function listClickableElements(): Promise<string> {
    const evalResult = await sendCommand('Runtime.evaluate', {
        expression: `(() => {
            const items = [];
            const seen = new Set();
            const els = document.querySelectorAll('a, button, [role="button"], [role="link"], [role="tab"], [role="menuitem"], input[type="submit"], input[type="button"], [onclick], [data-click], summary');
            els.forEach((el, i) => {
                if (i > 80) return; // Cap to avoid token overflow
                const rect = el.getBoundingClientRect();
                // Skip hidden/off-screen elements
                if (rect.width === 0 || rect.height === 0 || rect.top > window.innerHeight + 500) return;
                const tag = el.tagName.toLowerCase();
                let text = (el.textContent || '').trim().replace(/\\s+/g, ' ').substring(0, 80);
                if (!text) text = el.getAttribute('aria-label') || el.getAttribute('title') || el.getAttribute('alt') || '';
                if (!text) return; // Skip elements with no discernible text
                // Deduplicate by text
                const key = text.toLowerCase().substring(0, 40);
                if (seen.has(key)) return;
                seen.add(key);
                let info = tag;
                if (tag === 'a') {
                    const href = el.getAttribute('href') || '';
                    if (href && href !== '#' && !href.startsWith('javascript:')) {
                        info += ' href="' + href.substring(0, 60) + '"';
                    }
                }
                items.push('[' + info + '] "' + text + '"');
            });
            return items.join('\\n');
        })()`,
        returnByValue: true
    });

    try {
        const list = evalResult.result?.value || '';
        if (!list) return 'No clickable elements found on the page.';
        return `Clickable elements on this page:\\n${list}`;
    } catch {
        return 'Failed to list clickable elements.';
    }
}

/**
 * Click an element in the relay browser using a CSS selector OR text content.
 * 
 * CLICK STRATEGY (progressive fallback):
 *   1. Try CSS selector(s)
 *   2. Try text-based search on clickable elements
 *   3. Try aria-label search
 *   4. For the found element: get its bounding box and use CDP Input.dispatchMouseEvent
 *   5. If CDP mouse dispatch fails, fall back to el.click()
 */
export async function clickElement(selector: string): Promise<string> {
    // Pre-process on server side: extract text hints from :contains() patterns
    // and split comma-separated selectors for individual attempts
    const containsMatches = selector.match(/:contains\(['"]([^'"]+)['"]\)/gi) || [];
    const textHints = containsMatches.map(m => {
        const match = m.match(/:contains\(['"]([^'"]+)['"]\)/i);
        return match ? match[1] : '';
    }).filter((t): t is string => t !== undefined && t.length > 0);

    // Split comma-separated selectors and clean each one
    const rawSelectors = selector.split(',').map(s => s.trim()).filter(s => s.length > 0);
    // Filter out selectors with :contains() as they're not valid CSS
    const cssSelectors = rawSelectors
        .filter(s => !s.includes(':contains'))
        .map(s => s.replace(/'/g, "\\'"));

    // Combine text hints with the raw selector as fallback text
    const allTextSearches = [...new Set([...textHints, selector])];

    const escapedTexts = allTextSearches.map(t => (t || '').replace(/'/g, "\\'").replace(/\\/g, '\\\\')).join('|||');
    const escapedCss = cssSelectors.join('|||');

    // STEP 1: Find the element and get its bounding box coordinates
    const evalResult = await sendCommand('Runtime.evaluate', {
        expression: `(() => {
            let el = null;
            
            // Try 1: Each valid CSS selector individually
            const cssSelectors = '${escapedCss}'.split('|||').filter(s => s.length > 0);
            for (const sel of cssSelectors) {
                try { el = document.querySelector(sel); } catch(e) {}
                if (el) break;
            }
            
            // Try 2: Text-based search using extracted text hints
            if (!el) {
                const textSearches = '${escapedTexts}'.split('|||').filter(s => s.length > 0);
                const candidates = [...document.querySelectorAll('a, button, [role="button"], [role="link"], [role="tab"], [role="menuitem"], li, span, h1, h2, h3, h4, h5, label, input[type="submit"]')];
                for (const searchText of textSearches) {
                    const st = searchText.toLowerCase().trim();
                    // Skip CSS-like strings in text search
                    if (st.includes(':') || st.includes('[') || st.includes('.') || st.includes('#')) continue;
                    el = candidates.find(c => {
                        const t = (c.textContent || '').trim().toLowerCase();
                        return t === st || (st.length > 2 && t.includes(st));
                    }) || null;
                    if (el) break;
                }
            }
            
            // Try 3: Search by aria-label using text hints
            if (!el) {
                const textSearches = '${escapedTexts}'.split('|||').filter(s => s.length > 0);
                for (const searchText of textSearches) {
                    const st = searchText.toLowerCase().trim();
                    if (st.includes(':') || st.includes('[')) continue;
                    el = [...document.querySelectorAll('[aria-label]')].find(c => 
                        (c.getAttribute('aria-label') || '').toLowerCase().includes(st)
                    ) || null;
                    if (el) break;
                }
            }
            
            if (!el) return JSON.stringify({ success: false, error: 'Not found. Tried CSS: [${escapedCss}] and text: [${escapedTexts}]' });
            
            // Get bounding box for CDP mouse click
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            const rect = el.getBoundingClientRect();
            const cx = Math.round(rect.left + rect.width / 2);
            const cy = Math.round(rect.top + rect.height / 2);
            const pageUrl = window.location.href;
            
            return JSON.stringify({ 
                success: true, 
                tag: el.tagName, 
                text: (el.textContent || '').trim().substring(0, 100),
                cx: cx,
                cy: cy,
                pageUrl: pageUrl,
                needsCdpClick: true
            });
        })()`,
        returnByValue: true
    });

    try {
        const data = JSON.parse(evalResult.result?.value || '{}');
        if (!data.success) return `Error: ${data.error}. TIP: Use the EXACT visible text only, e.g. click "Players" not a:contains('Players'). Try list_elements to see all clickable items.`;

        const previousUrl = data.pageUrl || '';
        let clicked = false;

        // STEP 2: Human-like mouse movement + CDP click (Bézier curve path)
        // Mimics Google Antigravity / ghost-cursor style mouse pointer movement
        if (data.needsCdpClick && data.cx !== undefined && data.cy !== undefined) {
            // Ensure ghost cursor is injected on the current page
            if (!ghostCursorInjected) await injectGhostCursor();
            try {
                const targetX = data.cx;
                const targetY = data.cy;

                // Generate a Bézier curve path from a random start point to the target
                // Start from a random edge position (simulates cursor coming from elsewhere)
                const startX = lastMouseX ?? (Math.random() * 400 + 100);
                const startY = lastMouseY ?? (Math.random() * 300 + 100);

                // Generate human-like Bézier curve control points with overshoot
                const points = generateBezierPath(startX, startY, targetX, targetY);

                // Fire the visual animation on the page (runs entirely client-side)
                animateGhostCursor(points);

                // Dispatch mouseMoved events along the curve with variable timing
                for (let i = 0; i < points.length; i++) {
                    const p = points[i]!;
                    await sendCommand('Input.dispatchMouseEvent', {
                        type: 'mouseMoved',
                        x: Math.round(p.x),
                        y: Math.round(p.y),
                        button: 'none'
                    });
                    // Variable delay: faster in the middle, slower at start/end (like a real hand)
                    const progress = i / points.length;
                    const speedFactor = 1 - 4 * Math.pow(progress - 0.5, 2); // Bell curve
                    const delay = Math.floor(8 + (1 - speedFactor) * 17 + Math.random() * 5);
                    await new Promise(r => setTimeout(r, delay));
                }

                // Brief hover pause before clicking (120-350ms, like a human aiming)
                await new Promise(r => setTimeout(r, 120 + Math.floor(Math.random() * 230)));

                // Click with slight jitter (±2px, humans can't click the exact center)
                const jitterX = targetX + (Math.random() * 4 - 2);
                const jitterY = targetY + (Math.random() * 4 - 2);

                await sendCommand('Input.dispatchMouseEvent', {
                    type: 'mousePressed',
                    x: Math.round(jitterX),
                    y: Math.round(jitterY),
                    button: 'left',
                    clickCount: 1
                });
                // Random click-hold duration (40-120ms, humans don't release instantly)
                await new Promise(r => setTimeout(r, 40 + Math.floor(Math.random() * 80)));
                await sendCommand('Input.dispatchMouseEvent', {
                    type: 'mouseReleased',
                    x: Math.round(jitterX),
                    y: Math.round(jitterY),
                    button: 'left',
                    clickCount: 1
                });

                // Show visual click ripple effect
                await showClickEffect(jitterX, jitterY);

                // Track last mouse position for the next movement
                lastMouseX = targetX;
                lastMouseY = targetY;

                clicked = true;
                console.log(`[RelayBridge] 🖱️ Human-like Bézier click at (${targetX}, ${targetY}) on ${data.tag}: "${data.text?.substring(0, 40)}"`);
            } catch (e: any) {
                console.warn(`[RelayBridge] CDP mouse click failed: ${e.message}. Falling back to el.click()`);
            }
        }

        // STEP 3: Fallback — DOM el.click() if CDP mouse events failed
        if (!clicked) {
            await sendCommand('Runtime.evaluate', {
                expression: `(() => {
                    let el = null;
                    const cssSelectors = '${escapedCss}'.split('|||').filter(s => s.length > 0);
                    for (const sel of cssSelectors) {
                        try { el = document.querySelector(sel); } catch(e) {}
                        if (el) break;
                    }
                    if (!el) {
                        const textSearches = '${escapedTexts}'.split('|||').filter(s => s.length > 0);
                        const candidates = [...document.querySelectorAll('a, button, [role="button"], [role="link"], [role="tab"], [role="menuitem"], li, span')];
                        for (const searchText of textSearches) {
                            const st = searchText.toLowerCase().trim();
                            if (st.includes(':') || st.includes('[') || st.includes('.') || st.includes('#')) continue;
                            el = candidates.find(c => {
                                const t = (c.textContent || '').trim().toLowerCase();
                                return t === st || (st.length > 2 && t.includes(st));
                            }) || null;
                            if (el) break;
                        }
                    }
                    if (el) el.click();
                })()`,
                returnByValue: true
            });
            console.log(`[RelayBridge] DOM fallback click on ${data.tag}: "${data.text?.substring(0, 40)}"`);
        }

        // STEP 4: Smart post-click wait
        await waitAfterClick(previousUrl);

        return `Clicked ${data.tag}: "${data.text}"`;
    } catch {
        return 'Click action completed';
    }
}

/**
 * Execute arbitrary JavaScript in the relay browser.
 */
export async function executeJs(script: string): Promise<string> {
    const evalResult = await sendCommand('Runtime.evaluate', {
        expression: `(async () => {
            try {
                ${script}
            } catch(e) {
                return 'JS Error: ' + e.message;
            }
        })()`,
        returnByValue: true,
        awaitPromise: true
    });

    try {
        const value = evalResult.result?.value;
        if (value === undefined) return 'JavaScript executed successfully with no return value.';
        if (typeof value === 'object') return `JavaScript executed successfully. Result: ${JSON.stringify(value, null, 2)}`;
        return `JavaScript executed successfully. Result: ${value}`;
    } catch {
        return 'JavaScript execution completed.';
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

import { BrowserManager } from './manager';
import { Page, BrowserContext } from 'playwright-core';

/**
 * BrowserTool: Agent-friendly wrapper around BrowserManager.
 * Provides simple actions the LLM can request: navigate, click, type, read_content, screenshot, wait_for_user.
 * Uses a singleton BrowserManager instance shared across all worker agents.
 *
 * Anti-detection: All interactions use human-like timing (random delays, incremental scrolling)
 * to avoid triggering bot-detection heuristics on modern sites.
 */

// Singleton browser manager
let sharedManager: BrowserManager | null = null;

function getManager(): BrowserManager {
    if (!sharedManager) {
        sharedManager = new BrowserManager();
    }
    return sharedManager;
}

/** Random delay between min and max milliseconds — mimics human reaction time */
const humanDelay = (min = 300, max = 900) =>
    new Promise<void>(r => setTimeout(r, min + Math.floor(Math.random() * (max - min))));

export interface BrowseAction {
    /** The sub-action to perform */
    action: 'navigate' | 'click' | 'type' | 'read_content' | 'screenshot' | 'wait_for_user' | 'scroll' | 'close';
    /** URL to navigate to (for 'navigate') */
    url?: string | undefined;
    /** CSS selector for click/type targets */
    selector?: string | undefined;
    /** Text to type (for 'type') */
    text?: string | undefined;
    /** Optional message to show the user (for 'wait_for_user' — e.g. "Please log in to your account") */
    message?: string | undefined;
    /** Direction for scroll: 'up' or 'down' */
    direction?: 'up' | 'down' | undefined;
}

export class BrowserTool {
    private page: Page | null = null;
    private context: BrowserContext | null = null;

    /**
     * Execute a browser action. Returns a text description of the result.
     */
    async execute(action: BrowseAction): Promise<string> {
        try {
            switch (action.action) {
                case 'navigate':
                    return await this.doNavigate(action.url || '');
                case 'click':
                    return await this.doClick(action.selector || '');
                case 'type':
                    return await this.doType(action.selector || '', action.text || '');
                case 'read_content':
                    return await this.doReadContent(action.selector);
                case 'screenshot':
                    return await this.doScreenshot();
                case 'wait_for_user':
                    return await this.doWaitForUser(action.message || 'Please complete the required action in the browser.');
                case 'scroll':
                    return await this.doScroll(action.direction || 'down');
                case 'close':
                    return await this.doClose();
                default:
                    return `Unknown browser action: ${action.action}`;
            }
        } catch (e: any) {
            return `Browser action '${action.action}' failed: ${e.message}`;
        }
    }

    private async ensurePage(): Promise<Page> {
        if (this.page && !this.page.isClosed()) {
            return this.page;
        }

        const manager = getManager();
        this.context = await manager.getProfileContext('default');

        // Get existing pages or create a new one
        const pages = this.context.pages();
        const lastPage = pages.length > 0 ? pages[pages.length - 1] : undefined;
        if (lastPage) {
            this.page = lastPage;
        } else {
            this.page = await this.context.newPage();
        }

        // Set a reasonable viewport
        await this.page!.setViewportSize({ width: 1280, height: 900 });

        return this.page!;
    }

    private async doNavigate(url: string): Promise<string> {
        if (!url) return 'Error: No URL provided for navigate action.';

        const page = await this.ensurePage();

        // Add https:// if no protocol specified
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            url = 'https://' + url;
        }

        console.log(`[BrowserTool] Navigating to: ${url}`);
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 });

        // Human-like: wait for page activity to settle + random pause
        try { await page.waitForLoadState('networkidle', { timeout: 5000 }); } catch { }
        await humanDelay(800, 1800);

        // Move mouse to a random position on the page to trigger hover events
        const viewport = page.viewportSize();
        if (viewport) {
            await page.mouse.move(
                200 + Math.floor(Math.random() * (viewport.width - 400)),
                200 + Math.floor(Math.random() * (viewport.height - 400)),
                { steps: 5 }
            );
        }

        const title = await page.title();
        const currentUrl = page.url();

        return `Navigated to "${title}" (${currentUrl}). The browser window is now open and visible.`;
    }

    private async doClick(selector: string): Promise<string> {
        if (!selector) return 'Error: No selector provided for click action.';

        const page = await this.ensurePage();

        try {
            // Human-like: hover first, then pause, then click
            await page.hover(selector, { timeout: 5000 });
            await humanDelay(150, 400);
            await page.click(selector, { timeout: 5000, delay: 50 + Math.floor(Math.random() * 80) });
            await humanDelay(400, 1000);
            return `Clicked on element matching "${selector}". Page may have updated.`;
        } catch {
            // Try text-based selector as fallback
            try {
                await page.hover(`text="${selector}"`, { timeout: 3000 }).catch(() => {});
                await humanDelay(100, 300);
                await page.click(`text="${selector}"`, { timeout: 5000 });
                await humanDelay(400, 1000);
                return `Clicked on text "${selector}". Page may have updated.`;
            } catch (e: any) {
                return `Could not find element to click: "${selector}". Error: ${e.message}. Try using a different selector or reading the page content first.`;
            }
        }
    }

    private async doType(selector: string, text: string): Promise<string> {
        if (!selector) return 'Error: No selector provided for type action.';
        if (!text) return 'Error: No text provided for type action.';

        const page = await this.ensurePage();

        try {
            // Human-like: click first, small pause, then type with realistic WPM delay
            await page.click(selector, { timeout: 5000 });
            await humanDelay(200, 500);
            // Clear existing value then type with per-character delay (50–120ms ≈ 80–120 WPM)
            await page.fill(selector, '', { timeout: 3000 });
            await page.type(selector, text, { delay: 50 + Math.floor(Math.random() * 70) });
            return `Typed "${text.substring(0, 80)}${text.length > 80 ? '...' : ''}" into element "${selector}".`;
        } catch {
            try {
                const input = page.locator(selector).first();
                await input.click({ timeout: 3000 });
                await humanDelay(150, 400);
                await input.type(text, { delay: 60 + Math.floor(Math.random() * 60) });
                return `Typed "${text.substring(0, 80)}" into element "${selector}".`;
            } catch {
                try {
                    await page.keyboard.type(text, { delay: 70 });
                    return `Typed "${text.substring(0, 80)}" using keyboard input (no specific element targeted).`;
                } catch (e2: any) {
                    return `Failed to type into "${selector}": ${e2.message}`;
                }
            }
        }
    }

    private async doReadContent(selector?: string): Promise<string> {
        const page = await this.ensurePage();
        const title = await page.title();
        const currentUrl = page.url();

        let content: string;

        if (selector) {
            try {
                content = await page.locator(selector).first().innerText({ timeout: 5000 });
            } catch {
                content = await page.locator('body').innerText({ timeout: 5000 });
            }
        } else {
            // Extract meaningful text content, not raw HTML
            content = await page.evaluate(() => {
                // Remove script, style, nav, footer to focus on main content
                const clone = document.body.cloneNode(true) as HTMLElement;
                clone.querySelectorAll('script, style, nav, footer, header, noscript, iframe, svg').forEach(el => el.remove());

                // Get text content, clean up whitespace
                let text = clone.innerText || clone.textContent || '';
                // Collapse multiple newlines/spaces
                text = text.replace(/\n{3,}/g, '\n\n').replace(/[ \t]+/g, ' ').trim();
                return text;
            });
        }

        // Truncate to prevent token explosion.
        // 1,500 chars is enough to extract business names, addresses, phone numbers.
        // The agent can navigate to specific pages if it needs deeper detail.
        const MAX = 1500;
        if (content.length > MAX) {
            const head = content.substring(0, 1000);
            const tail = content.substring(content.length - 500);
            content = `${head}\n\n... [CONTENT TRUNCATED — use a targeted selector or navigate to a specific page for more detail] ...\n\n${tail}`;
        }

        return `Page: "${title}" (${currentUrl})\n\n${content}`;
    }

    private async doScreenshot(): Promise<string> {
        const page = await this.ensurePage();
        // Take screenshot but don't save it — just confirm it was taken
        // In a real implementation we could save to workspace and return the path
        const title = await page.title();
        const url = page.url();

        // Get a text summary of what's visible instead (more useful for the LLM)
        const visibleText = await page.evaluate(() => {
            const body = document.body;
            if (!body) return 'Empty page';

            // Get visible elements in viewport
            const elements: string[] = [];
            const walker = document.createTreeWalker(body, NodeFilter.SHOW_ELEMENT);
            let node;
            let count = 0;
            while ((node = walker.nextNode()) && count < 50) {
                const el = node as HTMLElement;
                const rect = el.getBoundingClientRect();
                if (rect.top >= 0 && rect.top < window.innerHeight && rect.width > 0 && rect.height > 0) {
                    const tag = el.tagName.toLowerCase();
                    const text = el.innerText?.trim().substring(0, 80);
                    if (text && ['a', 'button', 'h1', 'h2', 'h3', 'h4', 'p', 'input', 'textarea', 'select', 'li', 'td', 'th', 'span', 'div'].includes(tag)) {
                        const attrs: string[] = [];
                        if (el.id) attrs.push(`id="${el.id}"`);
                        if (el.className && typeof el.className === 'string') attrs.push(`class="${el.className.substring(0, 40)}"`);
                        if (tag === 'a') attrs.push(`href="${(el as HTMLAnchorElement).href?.substring(0, 60)}"`);
                        if (tag === 'input') attrs.push(`type="${(el as HTMLInputElement).type}" name="${(el as HTMLInputElement).name}"`);
                        elements.push(`<${tag}${attrs.length ? ' ' + attrs.join(' ') : ''}> ${text.substring(0, 60)}`);
                        count++;
                    }
                }
            }
            return elements.join('\n');
        });

        return `Viewport snapshot of "${title}" (${url}):\n\n${visibleText}`;
    }

    private async doWaitForUser(message: string): Promise<string> {
        const page = await this.ensurePage();
        const url = page.url();

        console.log(`\n🔴 [BrowserTool] WAITING FOR USER ACTION: ${message}`);
        console.log(`   Browser is open at: ${url}`);
        console.log(`   The agent will wait up to 120 seconds for you to complete the action.\n`);

        // Inject a visible overlay in the browser to prompt the user
        await page.evaluate((msg: string) => {
            const overlay = document.createElement('div');
            overlay.id = '__openspider_auth_overlay';
            overlay.innerHTML = `
                <div style="position:fixed;top:0;left:0;right:0;z-index:999999;background:linear-gradient(135deg,#1e40af,#7c3aed);padding:16px 24px;display:flex;align-items:center;justify-content:between;gap:16px;font-family:system-ui,-apple-system,sans-serif;box-shadow:0 4px 20px rgba(0,0,0,0.3);">
                    <div style="background:rgba(255,255,255,0.15);border-radius:12px;padding:8px 12px;">
                        <span style="font-size:24px;">🕷️</span>
                    </div>
                    <div style="flex:1;">
                        <div style="color:white;font-weight:700;font-size:14px;">OpenSpider Agent is waiting for you</div>
                        <div style="color:rgba(255,255,255,0.8);font-size:13px;margin-top:2px;">${msg}</div>
                    </div>
                    <button onclick="document.getElementById('__openspider_auth_overlay').remove()" style="background:rgba(255,255,255,0.2);border:1px solid rgba(255,255,255,0.3);color:white;padding:8px 20px;border-radius:8px;cursor:pointer;font-weight:600;font-size:13px;">
                        ✓ Done
                    </button>
                </div>
            `;
            document.body.appendChild(overlay);
        }, message);

        // Wait for the overlay to be removed (user clicked "Done") or timeout
        try {
            await page.waitForSelector('#__openspider_auth_overlay', { state: 'detached', timeout: 120000 });
            console.log(`[BrowserTool] User confirmed action completed.`);
        } catch {
            // Timeout — remove overlay and continue anyway
            console.log(`[BrowserTool] Wait timed out after 120s. Continuing...`);
            await page.evaluate(() => {
                const overlay = document.getElementById('__openspider_auth_overlay');
                if (overlay) overlay.remove();
            }).catch(() => { });
        }

        // Re-read the page state after user interaction
        const newTitle = await page.title();
        const newUrl = page.url();

        return `User interaction completed. Page is now: "${newTitle}" (${newUrl}). You can now proceed with reading content or navigating further.`;
    }

    private async doScroll(direction: 'up' | 'down'): Promise<string> {
        const page = await this.ensurePage();
        const totalScroll = 500 + Math.floor(Math.random() * 300);
        const steps = 4 + Math.floor(Math.random() * 4); // 4–7 incremental steps
        const stepSize = Math.floor(totalScroll / steps) * (direction === 'down' ? 1 : -1);

        // Incremental scrolling mimics a human using a mouse wheel
        for (let i = 0; i < steps; i++) {
            await page.evaluate((amount: number) => { window.scrollBy(0, amount); }, stepSize);
            await humanDelay(80, 200);
        }
        await humanDelay(300, 600);
        return `Scrolled ${direction} ~${totalScroll}px in ${steps} steps.`;
    }

    private async doClose(): Promise<string> {
        if (this.page && !this.page.isClosed()) {
            await this.page.close();
            this.page = null;
        }
        return 'Browser tab closed.';
    }
}

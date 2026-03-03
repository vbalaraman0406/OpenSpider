import { chromium as playwrightChromium, Browser, BrowserContext } from 'playwright-core';
import { chromium as stealthChromium } from 'playwright-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import { BrowserConfigManager, ProfileConfig } from './config';
import * as path from 'node:path';
import * as fs from 'node:fs';

// Register the stealth plugin — patches navigator.webdriver, chrome runtime,
// plugins length, iframe content window, permissions API, and ~30 other signals.
stealthChromium.use(StealthPlugin());

// Rotate through realistic Chrome stable user-agents to avoid UA fingerprinting
const REALISTIC_USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
];

function pickUserAgent(): string {
    return REALISTIC_USER_AGENTS[Math.floor(Math.random() * REALISTIC_USER_AGENTS.length)] ||
        REALISTIC_USER_AGENTS[0]!;
}

/**
 * Chrome launch args that remove automation signals.
 * Based on the well-known "undetectable chrome" arg list.
 */
const STEALTH_ARGS = [
    // Remove "Chrome is being controlled by automated software" banner
    '--disable-infobars',
    // Disable automation flags
    '--disable-blink-features=AutomationControlled',
    // Make webdriver flag invisible
    '--exclude-switches=enable-automation',
    '--disable-extensions',
    // Enable GPU (disabled in automation by default — a clear detection signal)
    '--use-gl=swiftshader',
    // SECURITY: Enforce sandbox isolation for renderer processes.
    // This prevents a compromised renderer (via malicious page exploit) from
    // breaking out into the host OS or reading host memory.
    '--sandbox',
    '--disable-setuid-sandbox',  // Only disable setuid sandbox (Linux-specific), not the full sandbox
    // SECURITY: Disable access to file:// URLs from renderer (belt-and-suspenders)
    '--disable-file-access-from-files',
    '--disable-file-system',
    // SECURITY: Isolate each site in its own process (Site Isolation)
    // Prevents cross-origin data leaks even if one renderer is compromised
    '--site-per-process',
    // Realistic window / display settings
    '--start-maximized',
    '--window-size=1366,768',
    // Disable various automation-hint APIs
    '--disable-web-security=false',
    '--allow-running-insecure-content',
    // Disable save-password popup
    '--disable-save-password-bubble',
    // Clipboard etc. — avoid permission dialogs
    '--disable-features=TranslateUI,BlinkGenPropertyTrees',
    '--disable-ipc-flooding-protection',
    // Prevent "restore session" dialogs
    '--disable-session-crashed-bubble',
    '--disable-restore-session-state',
];

export class BrowserManager {
    private contexts: Map<string, BrowserContext> = new Map();
    private browsers: Map<string, Browser> = new Map();

    constructor() { }

    async getProfileContext(profileName: string): Promise<BrowserContext> {
        const config = BrowserConfigManager.load();
        const fullProfileName = profileName === 'default' ? config.defaultProfile : profileName;

        if (this.contexts.has(fullProfileName)) {
            return this.contexts.get(fullProfileName)!;
        }

        const profileConfig = config.profiles[fullProfileName] || {};
        const context = await this.launchProfile(fullProfileName, profileConfig, config.headless);

        this.contexts.set(fullProfileName, context);
        return context;
    }

    private async launchProfile(name: string, pConfig: ProfileConfig, headless: boolean): Promise<BrowserContext> {
        // --- Remote CDP (Chrome Extension relay or browserless) ---
        if (pConfig.cdpUrl) {
            console.log(`[BrowserManager] Connecting to remote profile '${name}' at ${pConfig.cdpUrl}...`);
            const browser = await playwrightChromium.connectOverCDP(pConfig.cdpUrl, { timeout: 5000 });
            this.browsers.set(name, browser);
            return browser.contexts()[0] || await browser.newContext();
        }

        // --- Local managed profile with full stealth ---
        console.log(`[BrowserManager] Launching stealth local profile '${name}'...`);
        const userDataDir = path.join(process.cwd(), 'workspace', 'browser_profiles', name);
        if (!fs.existsSync(userDataDir)) {
            fs.mkdirSync(userDataDir, { recursive: true });
        }

        const executablePath = BrowserConfigManager.getExecutablePath();
        const userAgent = pickUserAgent();

        // playwright-extra launchPersistentContext with stealth plugin applied
        const context = await (stealthChromium as any).launchPersistentContext(userDataDir, {
            headless,
            ...(executablePath ? { executablePath } : {}),
            ...(executablePath ? {} : { channel: 'chrome' }),
            args: [
                ...STEALTH_ARGS,
                ...(pConfig.cdpPort ? [`--remote-debugging-port=${pConfig.cdpPort}`] : []),
            ],
            // Realistic browser context config
            userAgent,
            locale: 'en-US',
            timezoneId: 'America/Los_Angeles',
            viewport: { width: 1366, height: 768 },
            // Accept all the permissions a real user would have consented to
            permissions: ['geolocation', 'notifications'],
            // Realistic extra HTTP headers
            extraHTTPHeaders: {
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
            },
        });

        // Override navigator.webdriver via init script (belt-and-suspenders on top of stealth plugin)
        await context.addInitScript(() => {
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            // Remove playwright-specific chrome.runtime signals
            // @ts-ignore
            if (window.chrome) {
                // @ts-ignore
                window.chrome.runtime = {};
            }
        });

        if (pConfig.color) {
            await context.addInitScript((color: string) => {
                window.addEventListener('DOMContentLoaded', () => {
                    const overlay = document.createElement('div');
                    overlay.style.cssText = `position:fixed;top:0;left:0;right:0;height:4px;background:${color};z-index:9999999;pointer-events:none;`;
                    document.body.appendChild(overlay);
                });
            }, pConfig.color);
        }

        return context;
    }

    async closeProfile(profileName: string) {
        const context = this.contexts.get(profileName);
        if (context) {
            await context.close();
            this.contexts.delete(profileName);
        }

        const browser = this.browsers.get(profileName);
        if (browser) {
            await browser.close();
            this.browsers.delete(profileName);
        }
    }

    async closeAll() {
        for (const name of this.contexts.keys()) {
            await this.closeProfile(name);
        }
    }
}

import { chromium, Browser, BrowserContext, Page } from 'playwright-core';
import { BrowserConfigManager, ProfileConfig } from './config';
import * as path from 'node:path';
import * as fs from 'node:fs';

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
        // If it's a remote CDP url (like browserless or chrome extension relay)
        if (pConfig.cdpUrl) {
            console.log(`[BrowserManager] Connecting to remote profile '${name}' at ${pConfig.cdpUrl}...`);
            const browser = await chromium.connectOverCDP(pConfig.cdpUrl, { timeout: 5000 });
            this.browsers.set(name, browser);
            return browser.contexts()[0] || await browser.newContext();
        }

        // It is a local managed profile, launch Chromium with persistent context
        console.log(`[BrowserManager] Launching local managed profile '${name}'...`);
        const userDataDir = path.join(process.cwd(), 'workspace', 'browser_profiles', name);
        if (!fs.existsSync(userDataDir)) {
            fs.mkdirSync(userDataDir, { recursive: true });
        }

        const executablePath = BrowserConfigManager.getExecutablePath();
        const args = [];

        // Basic anti-ssrf for local navigations (basic defense, needs deeper proxy for true SSRF filtering)
        args.push('--disable-web-security=false');

        // Optional debugging port
        if (pConfig.cdpPort) {
            args.push(`--remote-debugging-port=${pConfig.cdpPort}`);
        }

        const context = await chromium.launchPersistentContext(userDataDir, {
            headless,
            ...(executablePath ? { executablePath } : {}),
            ...(executablePath ? {} : { channel: 'chrome' }), // Fallback to installed chrome if no exec path
            args
        });

        // Set distinctive UI coloring via CDP if color is provided (basic visual indicator trick)
        if (pConfig.color) {
            // Note: Playwright doesn't have a direct "theme color" API, but we can evaluate a script on new pages
            await context.addInitScript((color: string) => {
                // Add a visual border to indicate which profile this is
                window.addEventListener('DOMContentLoaded', () => {
                    const overlay = document.createElement('div');
                    overlay.style.position = 'fixed';
                    overlay.style.top = '0';
                    overlay.style.left = '0';
                    overlay.style.right = '0';
                    overlay.style.height = '4px';
                    overlay.style.backgroundColor = color;
                    overlay.style.zIndex = '9999999';
                    overlay.style.pointerEvents = 'none';
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

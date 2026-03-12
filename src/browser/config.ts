import * as fs from 'node:fs';
import * as path from 'node:path';
import * as os from 'node:os';

export interface ProfileConfig {
    cdpPort?: number;
    cdpUrl?: string;
    color?: string;
}

export interface BrowserConfig {
    enabled: boolean;
    defaultProfile: string;
    executablePath?: string;
    headless: boolean;
    remoteCdpTimeoutMs: number;
    ssrfPolicy: {
        dangerouslyAllowPrivateNetwork: boolean;
    };
    profiles: Record<string, ProfileConfig>;
}

// Auto-detect headless: Linux without DISPLAY (VPS/server) → headless, Mac/Windows → headed
const isHeadlessDefault = os.platform() === 'linux' && !process.env.DISPLAY;

const DEFAULT_CONFIG: BrowserConfig = {
    enabled: true,
    defaultProfile: 'openspider',
    headless: isHeadlessDefault,
    remoteCdpTimeoutMs: 3000,
    ssrfPolicy: {
        dangerouslyAllowPrivateNetwork: true
    },
    profiles: {
        openspider: {
            cdpPort: 18800,
            color: '#FF4500' // Orange like OpenSpider
        },
        chrome: {
            cdpUrl: 'http://127.0.0.1:18792', // Relay port
            color: '#4285F4'
        }
    }
};

export class BrowserConfigManager {
    static getConfigPath(): string {
        return path.join(process.cwd(), 'workspace', 'browser.json');
    }

    static load(): BrowserConfig {
        const configPath = this.getConfigPath();
        if (!fs.existsSync(configPath)) {
            // Write defaults
            fs.writeFileSync(configPath, JSON.stringify(DEFAULT_CONFIG, null, 2), 'utf-8');
            return DEFAULT_CONFIG;
        }

        try {
            const raw = fs.readFileSync(configPath, 'utf-8');
            const parsed = JSON.parse(raw);
            return { ...DEFAULT_CONFIG, ...parsed, profiles: { ...DEFAULT_CONFIG.profiles, ...(parsed.profiles || {}) } };
        } catch (e: any) {
            console.error('[BrowserConfig] Error parsing config, using defaults:', e.message);
            return DEFAULT_CONFIG;
        }
    }

    static save(config: BrowserConfig): void {
        const configPath = this.getConfigPath();
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf-8');
    }

    static getExecutablePath(): string {
        const config = this.load();
        if (config.executablePath && fs.existsSync(config.executablePath)) {
            return config.executablePath;
        }

        // Auto-detect common paths
        const isMac = os.platform() === 'darwin';
        const isWin = os.platform() === 'win32';

        if (isMac) {
            const paths = [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
                '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
            ];
            const found = paths.find(p => fs.existsSync(p));
            if (found) return found;
        } else if (isWin) {
            const paths = [
                'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
                'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
            ];
            const found = paths.find(p => fs.existsSync(p));
            if (found) return found;
        } else {
            // Linux — also check Playwright's bundled Chromium
            const paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable',
                '/usr/bin/brave-browser',
                '/usr/bin/chromium',
                '/usr/bin/chromium-browser',
            ];
            // Check Playwright's cache for bundled Chromium
            const playwrightCache = path.join(os.homedir(), '.cache', 'ms-playwright');
            if (fs.existsSync(playwrightCache)) {
                try {
                    const dirs = fs.readdirSync(playwrightCache).filter(d => d.startsWith('chromium-'));
                    for (const dir of dirs.sort().reverse()) {
                        const chromePath = path.join(playwrightCache, dir, 'chrome-linux64', 'chrome');
                        if (fs.existsSync(chromePath)) paths.unshift(chromePath);
                    }
                } catch (_) { }
            }
            const found = paths.find(p => fs.existsSync(p));
            if (found) return found;
        }

        // If Playwright handles it well, we might not strictly need this if we don't pass executablePath to launchPersistentContext
        return '';
    }
}

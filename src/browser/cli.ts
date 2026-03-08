import * as p from '@clack/prompts';
import { BrowserConfigManager, BrowserConfig } from './config';
import * as os from 'node:os';

function getLocalIp(): string {
    const interfaces = os.networkInterfaces();
    for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name] || []) {
            if (iface.family === 'IPv4' && !iface.internal) {
                // Prefer tailscale if available
                if (name.toLowerCase().includes('tailscale')) return iface.address;
            }
        }
    }
    // Fallback pass to just grab the first non-internal IPv4
    for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name] || []) {
            if (iface.family === 'IPv4' && !iface.internal) {
                return iface.address;
            }
        }
    }
    return '<YOUR_IP_ADDRESS>';
}

export async function runBrowserSetup() {
    console.clear();
    p.intro(`🕷️ OpenSpider Browser Specialist Configuration`);

    const config: BrowserConfig = BrowserConfigManager.load();

    const mode = await p.select({
        message: 'How would you like to configure the Browser Agent on THIS machine?',
        options: [
            { value: 'headless', label: '1. Run Headless (Server Mode)', hint: 'Runs invisibly in the background. Best for autonomous cloud operation.' },
            { value: 'visible', label: '2. Run Visibly (Local Mode)', hint: 'Runs Chromium visibly on your screen. Best for local development.' },
            { value: 'remote', label: '3. Connect to a Remote Client', hint: 'Cloud server securely tunnels to a Mac/PC and controls its browser.' }
        ]
    });

    if (p.isCancel(mode)) {
        p.cancel('Configuration cancelled.');
        process.exit(0);
    }

    if (mode === 'headless') {
        config.headless = true;
        config.defaultProfile = 'openspider';
        BrowserConfigManager.save(config);
        p.outro('✅ Browser configured to run in Headless mode on this server.');
        return;
    }

    if (mode === 'visible') {
        config.headless = false;
        config.defaultProfile = 'openspider';
        BrowserConfigManager.save(config);
        p.outro('✅ Browser configured to run Visibly on this machine.');
        return;
    }

    if (mode === 'remote') {
        p.log.info('You have chosen to control a remote browser (e.g. on your local Mac) from this OpenSpider server.');

        let macCmd = `/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --remote-allow-origins=*`;
        let winCmd = `"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --remote-allow-origins=*`;
        let linCmd = `google-chrome --remote-debugging-port=9222 --remote-allow-origins=*`;

        p.log.step(`STEP 1: On your CLIENT machine (your laptop), completely close all Chrome windows.
Then open a terminal and run the exact command below to restart Chrome with remote debugging opened:

🍏 Mac (Open the 'Terminal' app):
  ${macCmd}

🪟 Windows (Open 'Command Prompt'):
  ${winCmd}

🐧 Linux (Open your terminal emulator):
  ${linCmd}
`);

        const ipInput = await p.text({
            message: 'STEP 2: Enter the IP address (e.g. Tailscale IP) of the CLIENT machine you just started Chrome on:',
            placeholder: '100.100.100.100'
        });

        if (p.isCancel(ipInput)) {
            p.cancel('Configuration cancelled.');
            process.exit(0);
        }

        let ip = (ipInput as string).trim();
        if (ip.startsWith('http://') || ip.startsWith('https://')) {
            ip = ip.replace(/^https?:\/\//, '');
        }
        if (ip.includes(':')) {
            ip = ip.split(':')[0] || ''; // strip port if they provided it
        }

        const portInput = await p.text({
            message: 'Enter the remote debugging port used on the client (Default: 9222):',
            placeholder: '9222',
            initialValue: '9222'
        });

        if (p.isCancel(portInput)) {
            p.cancel('Configuration cancelled.');
            process.exit(0);
        }

        const port = (portInput as string).trim() || '9222';

        config.headless = false; // Doesn't matter for remote, but logically false
        config.defaultProfile = 'chrome';
        if (!config.profiles['chrome']) {
            config.profiles['chrome'] = {};
        }
        config.profiles['chrome'].cdpUrl = `http://${ip}:${port}`;

        BrowserConfigManager.save(config);
        p.outro(`✅ Configured to remotely control browser at http://${ip}:${port}.\nEnsure your server has network access to this IP (e.g. both machines are connected to Tailscale).`);
        return;
    }
}

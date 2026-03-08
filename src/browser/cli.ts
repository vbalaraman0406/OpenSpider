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
            { value: 'remote', label: '3. Connect to a Remote Client', hint: 'Cloud server securely tunnels to a Mac/PC and controls its browser.' },
            { value: 'client_setup', label: '4. Setup as Client (Show Instructions)', hint: 'Show instructions on how to prepare this Mac/PC to be remotely controlled.' }
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
        const ipInput = await p.text({
            message: 'Enter the IP address (e.g. Tailscale IP) of the Mac/PC you want to control:',
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
            message: 'Enter the remote debugging port (Default: 9222):',
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
        p.outro(`✅ Configured to remotely control browser at http://${ip}:${port}.\nMake sure the client machine is running Chrome with --remote-debugging-port=${port} and --remote-allow-origins=*`);
        return;
    }

    if (mode === 'client_setup') {
        const localIp = getLocalIp();

        p.log.info('To allow a remote OpenSpider cloud server to securely tunnel into this machine and use its residential browser profile, you must start Google Chrome from the terminal with remote debugging enabled.');

        p.log.step('Close all existing Google Chrome windows completely (Cmd+Q on Mac).');

        let launchCommand = '';
        if (os.platform() === 'darwin') {
            launchCommand = `/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --remote-allow-origins=*`;
        } else if (os.platform() === 'win32') {
            launchCommand = `"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --remote-allow-origins=*`;
        } else {
            launchCommand = `google-chrome --remote-debugging-port=9222 --remote-allow-origins=*`;
        }

        p.log.step(`Run this command in a new terminal tab:\n\n  ${launchCommand}\n`);

        p.log.step(`Then, on your OpenSpider **UBUNTU SERVER**, run 'openspider tools browser' \nand select "Connect to a Remote Client". Enter your machine's IP address when prompted:\n\n  Your local IP: ${localIp} (Make sure your Cloud Server can reach this, e.g. via Tailscale)`);

        p.outro('Client instructions complete.');
    }
}

import fs from 'node:fs';
import path from 'node:path';
import 'dotenv/config'; // Automatically loads .env if it exists

import { runSetup } from './setup';
import { startServer } from './server';
import { startWhatsApp } from './whatsapp';
import { initWorkspace } from './memory';

export async function bootstrap() {
    console.clear();
    console.log("🕷️ Starting OpenSpider Engine...");

    const rootDir = __dirname.endsWith('src') || __dirname.endsWith('dist') ? path.join(__dirname, '..') : __dirname;
    const envPath = path.join(rootDir, '.env');

    // 1. Run Setup Wizard if no configuration exists
    if (!fs.existsSync(envPath)) {
        console.log("No .env found. Running First-Time Setup Wizard...");
        await runSetup();

        // Reload environment variables after setup
        require('dotenv').config({ path: envPath });
    }

    // Synchronize the API Key to the Dashboard's Vite environment
    if (process.env.DASHBOARD_API_KEY) {
        const dashEnvPath = path.join(rootDir, 'dashboard', '.env');
        try {
            fs.writeFileSync(dashEnvPath, `VITE_API_KEY=${process.env.DASHBOARD_API_KEY.trim()}`);
        } catch (e) { }
    }

    // 2. Start the API & WebSocket Dashboard Server
    console.log("Initializing Workspace & Dashboard API Server...");
    initWorkspace();
    startServer();

    // 3. Start the WhatsApp Gateway conditionally
    let enableWhatsApp = process.env.ENABLE_WHATSAPP !== 'false'; // Default true unless env overrides
    try {
        const configPath = path.join(process.cwd(), 'workspace', 'whatsapp_config.json');
        if (fs.existsSync(configPath)) {
            const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
            if (config.enabled === false) {
                enableWhatsApp = false;
            }
        } else {
            // New installations without a config file yet shouldn't crash loop on QR timeouts.
            // Require explicit enablement via dashboard first.
            enableWhatsApp = false;
        }
    } catch (e) { }

    if (enableWhatsApp) {
        console.log("Initializing WhatsApp Baileys Client...");
        startWhatsApp();
    } else {
        console.log("WhatsApp Channel Disabled or Not Configured. Skipping Baileys initialization.");
    }
}

// Only auto-run if executed directly via ts-node or node (not when imported)
if (require.main === module) {
    bootstrap().catch(console.error);
}

import fs from 'node:fs';
import path from 'node:path';
import 'dotenv/config'; // Automatically loads .env if it exists

import { runSetup } from './setup';
import { startServer } from './server';
import { startWhatsApp } from './whatsapp';

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

    // 2. Start the API & WebSocket Dashboard Server
    console.log("Initializing Dashboard API Server...");
    startServer();

    // 3. Start the WhatsApp Gateway
    if (process.env.ENABLE_WHATSAPP !== 'false') {
        console.log("Initializing WhatsApp Baileys Client...");
        startWhatsApp();
    } else {
        console.log("WhatsApp Channel Disabled via .env configuration.");
    }
}

// Only auto-run if executed directly via ts-node or node (not when imported)
if (require.main === module) {
    bootstrap().catch(console.error);
}

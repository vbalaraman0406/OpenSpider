import fs from 'node:fs';
import path from 'node:path';
import 'dotenv/config'; // Automatically loads .env if it exists

import { runSetup } from './setup';
import { startServer } from './server';
import { startWhatsApp } from './whatsapp';

async function bootstrap() {
    console.clear();
    console.log("🕷️ Starting OpenSpider Engine...");

    const envPath = path.join(process.cwd(), '.env');

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
    console.log("Initializing WhatsApp Baileys Client...");
    startWhatsApp();
}

bootstrap().catch(console.error);

import makeWASocket, { DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } from '@whiskeysockets/baileys';
import * as qrcode from 'qrcode-terminal';
import { Boom } from '@hapi/boom';
import { ManagerAgent } from './agents/ManagerAgent';

export async function startWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('baileys_auth_info');
    const manager = new ManagerAgent();

    const { version, isLatest } = await fetchLatestBaileysVersion();
    console.log(`[WhatsApp] Using WA v${version.join('.')}, isLatest: ${isLatest}`);

    const sock = makeWASocket({
        version,
        printQRInTerminal: true,
        auth: state,
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            console.log("\n🕷️ [WhatsApp] Scan this QR code to connect OpenSpider:");
            qrcode.generate(qr, { small: true });
        }

        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect?.error as Boom)?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('Connection closed due to ', lastDisconnect?.error, ', reconnecting ', shouldReconnect);
            if (shouldReconnect) {
                startWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('🕷️ OpenSpider connected to WhatsApp!');
        }
    });

    sock.ev.on('messages.upsert', async (m) => {
        const msg = m.messages[0];
        if (!msg) return;

        // Ignore own messages or automated broadcasts
        if (!msg.message || msg.key.fromMe) return;

        // Ensure it's a text message
        const textMessage = msg.message.conversation || msg.message.extendedTextMessage?.text;
        if (!textMessage) return;

        console.log(`\n\n[WhatsApp] Received message from ${msg.key.remoteJid}: ${textMessage}`);

        // Acknowledge receipt
        await sock.sendMessage(msg.key.remoteJid!, { text: '🕷️ OpenSpider is processing your request...' });

        try {
            // Send to the Manager Agent
            const response = await manager.processUserRequest(textMessage);

            // Send result back to WhatsApp
            await sock.sendMessage(msg.key.remoteJid!, { text: `✅ *Task Complete*\n\n${response}` });
        } catch (error: any) {
            await sock.sendMessage(msg.key.remoteJid!, { text: `❌ *Error processing request:*\n${error.message}` });
        }
    });
}

export async function onboardWhatsApp(): Promise<void> {
    return new Promise(async (resolve, reject) => {
        console.log("🕷️ Initializing WhatsApp connection for Setup...");
        const { state, saveCreds } = await useMultiFileAuthState('baileys_auth_info');

        const { version } = await fetchLatestBaileysVersion();
        const sock = makeWASocket({
            version,
            printQRInTerminal: true,
            auth: state,
        });

        sock.ev.on('creds.update', saveCreds);

        sock.ev.on('connection.update', (update) => {
            const { connection, lastDisconnect, qr } = update;

            if (qr) {
                console.log("\n🕷️ [WhatsApp] Scan this QR code to connect OpenSpider:");
                qrcode.generate(qr, { small: true });
            }

            if (connection === 'close') {
                const shouldReconnect = (lastDisconnect?.error as Boom)?.output?.statusCode !== DisconnectReason.loggedOut;
                if (!shouldReconnect) {
                    reject(new Error("Logged out from WhatsApp."));
                }
            } else if (connection === 'open') {
                console.log('✅ OpenSpider successfully connected to WhatsApp!');
                resolve();
            }
        });
    });
}

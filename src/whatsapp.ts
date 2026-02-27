import makeWASocket, { DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } from '@whiskeysockets/baileys';
import * as qrcode from 'qrcode-terminal';
import { Boom } from '@hapi/boom';
import { ManagerAgent } from './agents/ManagerAgent';
import { PersonaShell } from './agents/PersonaShell';

let globalSocket: any = null;

export async function getParticipatingGroups(): Promise<Array<{ id: string, subject: string }>> {
    if (!globalSocket) return [];
    try {
        const groups = await globalSocket.groupFetchAllParticipating();
        return Object.values(groups).map((g: any) => ({
            id: g.id,
            subject: g.subject || 'Unknown Group'
        }));
    } catch (e) {
        console.error("[WhatsApp] Failed to fetch participating groups", e);
        return [];
    }
}

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

    globalSocket = sock;

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

        // Ensure we extract text from standard chat, extended chat, or media captions
        const textMessage = msg.message.conversation || msg.message.extendedTextMessage?.text || msg.message.imageMessage?.caption || '';
        const isGroup = msg.key.remoteJid?.endsWith('@g.us');

        // Dynamically ascertain the Manager's Persona Name
        let agentName = 'OpenSpider';
        try {
            const persona = new PersonaShell('manager');
            const caps = persona.getCapabilities();
            if (caps && caps.name) agentName = caps.name;
        } catch (e) { }

        let config = { dmPolicy: 'allowlist', allowedDMs: [] as string[], groupPolicy: 'disabled', allowedGroups: [] as string[], botMode: 'mention' };

        try {
            const configPath = './workspace/whatsapp_config.json';
            const fs = await import('node:fs');
            if (fs.existsSync(configPath)) {
                config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
            }
        } catch (e) { console.error("[WhatsApp] Failed to load Security Config. Defaulting to strict."); }

        // --- SECURITY FIREWALL ---
        if (isGroup) {
            // Group Policy Check
            if (config.groupPolicy === 'disabled') {
                return; // Block all group messages entirely
            } else if (config.groupPolicy === 'allowlist') {
                if (!config.allowedGroups.includes(msg.key.remoteJid!)) {
                    return; // Block, this group is not on the whitelist
                }
            }
            // If 'open', fall through and allow.

            // Group Chat Mentions logic
            if (config.botMode === 'mention') {
                const botNumber = sock.user?.id ? sock.user.id.split(':')[0] : '';
                const botJid = `${botNumber}@s.whatsapp.net`;

                const mentionedJidList = msg.message.extendedTextMessage?.contextInfo?.mentionedJid || [];
                const isTaggedViaJid = mentionedJidList.includes(botJid);
                const isMentionedViaText = textMessage.toLowerCase().includes(`@${agentName.toLowerCase()}`);

                // If not tagged via WhatsApp mention system AND not mentioned by plain text, ignore
                if (!isTaggedViaJid && !isMentionedViaText) {
                    return;
                }
            }
        } else {
            // DM Policy Check (Direct Messages)
            if (config.dmPolicy === 'disabled') {
                return; // Block all DMs
            } else if (config.dmPolicy === 'allowlist') {
                // Sender JID looks like '1234567890@s.whatsapp.net'
                const senderNumber = msg.key.remoteJid?.split('@')[0] || '';
                // Ensure the number is allowed, either exact literal '1234567890' or standard '+' format
                const hasMatch = config.allowedDMs.some(allowed =>
                    allowed.replace(/\D/g, '') === senderNumber.replace(/\D/g, '')
                );
                if (!hasMatch) {
                    return; // Block, sender not whitelisted
                }
            }
        }
        // --- END FIREWALL ---

        // We require either text or image
        const imageMessage = msg.message.imageMessage || msg.message.extendedTextMessage?.contextInfo?.quotedMessage?.imageMessage;
        if (!textMessage && !imageMessage) return;

        console.log(`\n\n[WhatsApp] Received message from ${msg.key.remoteJid}: ${textMessage}`);

        // Extract Media Payload
        let mediaBase64String: string | undefined = undefined;
        if (imageMessage) {
            try {
                // @whiskeysockets/baileys exports downloadMediaMessage natively 
                const { downloadMediaMessage } = await import('@whiskeysockets/baileys');
                const buffer = await downloadMediaMessage(
                    msg,
                    'buffer',
                    {},
                    {
                        logger: console as any,
                        reuploadRequest: sock.updateMediaMessage
                    }
                ) as Buffer;
                mediaBase64String = `data:${imageMessage.mimetype};base64,${buffer.toString('base64')}`;
                console.log(`[WhatsApp] Extracted multimodal image buffer payload!`);
            } catch (err) {
                console.error("[WhatsApp] Failed to decrypt media message payload:", err);
            }
        }

        // Acknowledge receipt
        await sock.sendMessage(msg.key.remoteJid!, { text: '🕷️ Processing your request...' });

        try {
            // Send to the Manager Agent
            // Note: ManagerAgent expects images array in updated implementation
            const response = await manager.processUserRequest(textMessage, mediaBase64String ? [mediaBase64String] : []);

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

        globalSocket = sock;

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

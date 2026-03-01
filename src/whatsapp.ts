import makeWASocket, { DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } from '@whiskeysockets/baileys';
import * as qrcode from 'qrcode-terminal';
import { Boom } from '@hapi/boom';
import { ManagerAgent } from './agents/ManagerAgent';
import { PersonaShell } from './agents/PersonaShell';
import fs from 'node:fs';
import path from 'node:path';

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

export async function sendWhatsAppMessage(jid: string, text: string) {
    if (!globalSocket) throw new Error("WhatsApp socket not connected");
    await globalSocket.sendMessage(jid, { text });
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
            try {
                const qrPath = path.join(__dirname, '..', '.latest_qr.txt');
                fs.writeFileSync(qrPath, qr, 'utf-8');
            } catch (e) { }
        }

        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect?.error as Boom)?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('Connection closed due to ', lastDisconnect?.error, ', reconnecting ', shouldReconnect);
            if (shouldReconnect) {
                startWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('🕷️ OpenSpider connected to WhatsApp!');
            try {
                const qrPath = path.join(__dirname, '..', '.latest_qr.txt');
                if (fs.existsSync(qrPath)) {
                    fs.unlinkSync(qrPath);
                }
            } catch (e) { }
        }
    });

    sock.ev.on('messages.upsert', async (m) => {
        const msg = m.messages[0];
        if (!msg) return;

        // We ignore automated broadcasts/status updates
        if (!msg.message || msg.key.remoteJid === 'status@broadcast') return;

        // Ensure we extract text from standard chat, extended chat, or media captions
        const textMessage = msg.message.conversation || msg.message.extendedTextMessage?.text || msg.message.imageMessage?.caption || msg.message.pollCreationMessage?.name || '';

        console.log(`\n[DEBUG - RAW WA MSG] fromMe: ${msg.key.fromMe}, remoteJid: ${msg.key.remoteJid}, text: ${textMessage}`);
        const isGroup = msg.key.remoteJid?.endsWith('@g.us');

        let isNoteToSelf = false;
        // Prevent Infinite Loops: If the message is from us AND starts with a known bot prefix or includes a bot signature, ignore it.
        // This allows the user to use the 'Message Yourself' feature to talk to the bot!
        if (msg.key.fromMe) {
            // Check if this was a message sent BY the Baileys socket (bot reply) vs a message typed by the human on their phone
            if (msg.message?.extendedTextMessage?.contextInfo?.isForwarded) return;

            // Strict heuristic: If the text message contains our Agent prefix or signature, drop it to avoid infinite loop
            if (textMessage.includes('[Agent]') || textMessage.startsWith('🤖') || textMessage.includes('OpenSpider') || textMessage.startsWith('✨ *')) {
                return;
            }

            const botNumber = sock.user?.id ? sock.user.id.split(':')[0] : '';
            isNoteToSelf = !!(msg.key.remoteJid?.includes('@lid') || msg.key.remoteJid?.startsWith(botNumber || ''));
            if (!isNoteToSelf) {
                return; // Ignore outbound messages sent to other people
            }
        }

        // Handle incoming reactions (just log them for context)
        if (msg.message.reactionMessage) {
            console.log(`[WhatsApp] Received Reaction: ${msg.message.reactionMessage.text} on message ${msg.message.reactionMessage.key?.id}`);
            return;
        }

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
        if (!isNoteToSelf) {
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
        }
        // --- END FIREWALL ---

        // We require either text or image
        const imageMessage = msg.message.imageMessage || msg.message.extendedTextMessage?.contextInfo?.quotedMessage?.imageMessage;
        if (!textMessage && !imageMessage) return;

        // --- MESSAGE LOGGING & FIREWALL ---
        console.log(`\n\n[You] 📱 (WhatsApp) ${textMessage}`);

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

        const botIdString = sock.user?.id ? sock.user.id.split(':')[0] : '';
        const replyJid = (isNoteToSelf && msg.key.remoteJid?.includes('@lid')) ? `${botIdString}@s.whatsapp.net` : msg.key.remoteJid!;

        // Acknowledge receipt natively with a typing indicator instead of a reaction
        try {
            await sock.sendPresenceUpdate('composing', replyJid);
        } catch (e) { }

        try {
            // Send to the Manager Agent
            // Note: ManagerAgent expects images array in updated implementation
            const response = await manager.processUserRequest(textMessage, mediaBase64String ? [mediaBase64String] : []);

            // Convert GitHub markdown to WhatsApp proprietary formatting
            let cleanResponse = response.replace(/\[Agent\] Plan execution finished successfully\. Final Output:?[\s\n]*/g, '');

            // 1. Convert **bold** to *bold*
            cleanResponse = cleanResponse.replace(/\*\*(.*?)\*\*/g, '*$1*');
            // 2. Convert # Headers to *Headers*
            cleanResponse = cleanResponse.replace(/^#+\s+(.*)$/gm, '*$1*');
            // 3. Convert [Link](url) to Link: url
            cleanResponse = cleanResponse.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1: $2');

            // Check if the LLM decided to send a Poll
            if (cleanResponse.includes('[POLL]')) {
                const pollMatch = cleanResponse.match(/\[POLL\](.*?)\[\/POLL\]/s);
                if (pollMatch && pollMatch[1]) {
                    const params = pollMatch[1].split('|').map(p => p.trim());
                    const pollName = params[0];
                    const options = params.slice(1).filter(Boolean);

                    if (pollName && options.length > 1) {
                        await sock.sendMessage(msg.key.remoteJid!, {
                            poll: {
                                name: pollName,
                                values: options.slice(0, 12), // WA allows max 12 options
                                selectableCount: 1
                            }
                        });
                        cleanResponse = cleanResponse.replace(pollMatch[0], '').trim();
                    }
                }
            }

            if (cleanResponse.length > 0) {
                // Broadcast to Web Dashboard UI!
                console.log(`\n[Agent] ${cleanResponse.trim()}`);

                // Send result back to WhatsApp with sleek dynamic header
                await sock.sendMessage(replyJid, { text: `✨ *${agentName}*\n\n${cleanResponse.trim()}` });
            }

            // Clear typing indicator
            await sock.sendPresenceUpdate('paused', replyJid);

        } catch (error: any) {
            await sock.sendPresenceUpdate('paused', replyJid);
            await sock.sendMessage(replyJid, { text: `❌ *Error processing request:*\n${error.message}` });
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

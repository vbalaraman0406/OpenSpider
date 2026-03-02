import makeWASocket, { DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion, WAMessageStubType } from '@whiskeysockets/baileys';
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

    const pino = require('pino');
    const NodeCache = require('node-cache');
    const msgRetryCounterCache = new NodeCache();

    const sock = makeWASocket({
        version,
        printQRInTerminal: true,
        auth: state,
        logger: pino({ level: 'error' }),
        markOnlineOnConnect: true,
        syncFullHistory: false,
        msgRetryCounterCache,
        getMessage: async (key) => {
            return { conversation: '' } as any;
        }
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
            // Discover the bot's own Linked Identity JID for self-message detection
            const userInfo = sock.user as any;
            if (userInfo?.lid) {
                // Strip device suffix (e.g. "150457066512456:32@lid" → "150457066512456@lid")
                myLid = userInfo.lid.replace(/:\d+@/, '@');
                console.log(`[WhatsApp] Bot LID discovered: ${myLid}`);
            } else if (userInfo?.id) {
                console.log(`[WhatsApp] Bot ID: ${userInfo.id}, LID not in sock.user — will try creds`);
            }
            // Try reading LID from auth state creds
            if (!myLid) {
                try {
                    const credsPath = path.join(process.cwd(), 'baileys_auth_info', 'creds.json');
                    if (fs.existsSync(credsPath)) {
                        const creds = JSON.parse(fs.readFileSync(credsPath, 'utf-8'));
                        if (creds.me?.lid) {
                            myLid = creds.me.lid.replace(/:\d+@/, '@');
                            console.log(`[WhatsApp] Bot LID discovered from creds: ${myLid}`);
                        }
                    }
                } catch (e) { }
            }
            if (!myLid) {
                console.warn(`[WhatsApp] ⚠️ Could not discover Bot LID. "Message Yourself" may not work until next reconnect. This is normal on first-ever connection.`);
            }
            try {
                const qrPath = path.join(__dirname, '..', '.latest_qr.txt');
                if (fs.existsSync(qrPath)) {
                    fs.unlinkSync(qrPath);
                }
            } catch (e) { }
        }
    });

    // Bot's own Linked Identity JID — discovered on connection or creds update
    let myLid = '';

    // Live LID discovery: Baileys writes the LID to creds after the first key exchange.
    // For a brand-new install, sock.user.lid may not exist on the first connection,
    // but creds.update fires once the server provides it.
    sock.ev.on('creds.update', () => {
        if (myLid) return; // Already discovered
        try {
            const credsPath = path.join(process.cwd(), 'baileys_auth_info', 'creds.json');
            if (fs.existsSync(credsPath)) {
                const creds = JSON.parse(fs.readFileSync(credsPath, 'utf-8'));
                if (creds.me?.lid) {
                    myLid = creds.me.lid.replace(/:\d+@/, '@');
                    console.log(`[WhatsApp] Bot LID discovered via creds update: ${myLid}`);
                }
            }
        } catch (e) { }
    });

    // Local LRU Caches to prevent Double-Messages and Infinite Loops
    const processedMessageIds = new Set<string>();
    const sentMessageIds = new Set<string>();

    sock.ev.on('messages.upsert', async (m) => {
        // Only process real-time incoming messages, avoid historical sync appends which cause Double-Messages
        if (m.type !== 'notify') return;

        const msg = m.messages[0];
        if (!msg || typeof msg.key.id !== 'string') return;

        // Message Deduplication Check (Do not add to cache yet!)
        if (processedMessageIds.has(msg.key.id!)) return;

        // We ignore automated broadcasts/status updates
        if (!msg.message || msg.key.remoteJid === 'status@broadcast') return;

        // Ensure we extract text from standard chat, extended chat, or media captions
        const textMessage = msg.message.conversation || msg.message.extendedTextMessage?.text || msg.message.imageMessage?.caption || msg.message.pollCreationMessage?.name || '';

        console.log(`\n[DEBUG - RAW WA MSG] fromMe: ${msg.key.fromMe}, remoteJid: ${msg.key.remoteJid}, text: ${textMessage}`);
        const isGroup = msg.key.remoteJid?.endsWith('@g.us');

        let isNoteToSelf = false;
        // Prevent Infinite Loops without hardcoded signatures:
        // By tracking the exact ID of messages sent by OpenSpider, we can drop echoed bot replies but allow 'Message Yourself' inputs from the human.
        if (msg.key.fromMe) {
            // Check if this was a forwarded message etc
            if (msg.message?.extendedTextMessage?.contextInfo?.isForwarded) return;

            // Strict heuristic perfectly mirroring OpenClaw's design pattern:
            if (sentMessageIds.has(msg.key.id!)) {
                return; // OpenSpider sent this! Drop it to prevent the infinite loop echo!
            }

            const botNumber = sock.user?.id ? sock.user.id.split(':')[0] : '';
            // Self-message detection:
            // 1. remoteJid starts with the bot's own phone number (standard @s.whatsapp.net)
            // 2. remoteJid matches the bot's own cached LID (discovered on connection from creds)
            isNoteToSelf = !!(
                (botNumber && msg.key.remoteJid?.startsWith(botNumber)) ||
                (myLid && msg.key.remoteJid === myLid)
            );
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

        let config = { dmPolicy: 'allowlist', allowedDMs: [] as string[], groupPolicy: 'disabled', allowedGroups: [] as any[], botMode: 'mention' };

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
                    // allowedGroups can be: string[] or { jid: string, mode: string }[]
                    const matchedGroup = config.allowedGroups.find((g: any) => {
                        const jid = typeof g === 'string' ? g : g.jid;
                        return jid === msg.key.remoteJid;
                    });
                    if (!matchedGroup) {
                        return; // Block, this group is not on the whitelist
                    }
                    // Determine per-group mode (default to global botMode for backward compat)
                    const groupMode = typeof matchedGroup === 'string'
                        ? (config.botMode || 'mention')
                        : (matchedGroup.mode || config.botMode || 'mention');

                    // Group Chat Mentions logic (per-group)
                    if (groupMode === 'mention') {
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
                    // If groupMode === 'listen', fall through and process every message
                } else if (config.groupPolicy === 'open') {
                    // For open policy, use global botMode for mention check
                    if (config.botMode === 'mention') {
                        const botNumber = sock.user?.id ? sock.user.id.split(':')[0] : '';
                        const botJid = `${botNumber}@s.whatsapp.net`;

                        const mentionedJidList = msg.message.extendedTextMessage?.contextInfo?.mentionedJid || [];
                        const isTaggedViaJid = mentionedJidList.includes(botJid);
                        const isMentionedViaText = textMessage.toLowerCase().includes(`@${agentName.toLowerCase()}`);

                        if (!isTaggedViaJid && !isMentionedViaText) {
                            return;
                        }
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

        // Fast-path composing trigger: Fire instantly before the Ghost Trap so messages show a typing
        // bubble instantaneously while Baileys negotiates the Bad MAC retry in the background.
        // For @lid JIDs (self-message device proxies), reroute composing to the bot's primary JID.
        if (msg.key.remoteJid) {
            const botIdStr = sock.user?.id ? sock.user.id.split(':')[0] : '';
            const composingTarget = msg.key.remoteJid.includes('@lid')
                ? `${botIdStr}@s.whatsapp.net`
                : msg.key.remoteJid;
            sock.sendPresenceUpdate('composing', composingTarget).catch(() => { });
        }

        // 🔥 BAD MAC NUCLEAR GHOST TRAP 🔥
        // 'Message Yourself' packets occasionally de-sync end-to-end encryption ratchets.
        // Libsignal throws a "Bad MAC" error internally and completely strips the payload.
        // If we get an empty message from the user natively, it's a ghost packet.
        // We drop it here BEFORE adding its ID to the LRU deduplication cache!
        // This allows Baileys' native `msgRetryCounterCache` to securely negotiate a fresh key with Meta,
        // and Meta will instantly re-send the payload with the EXACT same msg ID safely seconds later!
        if (msg.key.fromMe && !imageMessage && textMessage.trim() === '') {
            return;
        }

        if (!textMessage && !imageMessage) return;

        // Now that we verified this is a real, decrypted payload, add it to the LRU cache so we never process it twice!
        processedMessageIds.add(msg.key.id!);
        if (processedMessageIds.size > 5000) processedMessageIds.delete(Array.from(processedMessageIds)[0]!);

        // --- MESSAGE LOGGING & FIREWALL ---
        console.log(`[You] 📱 (WhatsApp) ${textMessage}`);

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
        const botJid = `${botIdString}@s.whatsapp.net`;

        // For self-messages, the remoteJid often arrives as an @lid device proxy which is
        // invisible in the chat UI. Route replies to the bot's primary @s.whatsapp.net JID
        // so messages actually appear in the "Message Yourself" chat window.
        const replyJid = (isNoteToSelf && msg.key.remoteJid?.includes('@lid'))
            ? botJid
            : msg.key.remoteJid!;

        // Acknowledge receipt natively with a continuous typing indicator heartbeat
        // Following OpenClaw's pattern: always attempt composing, silently catch failures.
        let composingInterval: NodeJS.Timeout | null = null;
        try {
            await sock.sendPresenceUpdate('composing', replyJid);
            composingInterval = setInterval(() => {
                sock.sendPresenceUpdate('composing', replyJid).catch(() => { });
            }, 8000);
        } catch (e) {
            // Silently swallow — Meta may reject composing for self-JIDs but connection stays alive
        }

        try {
            // Send to the Manager Agent
            // Note: ManagerAgent expects images array in updated implementation
            const groupContextPrefix = isGroup ? `[GROUP CHAT] You are responding in a WhatsApp group chat. People can talk to you by tagging you as @${agentName}. Keep this in mind when introducing yourself or giving instructions.\n\n` : '';
            const response = await manager.processUserRequest(groupContextPrefix + textMessage, mediaBase64String ? [mediaBase64String] : []);

            if (composingInterval) clearInterval(composingInterval);

            // Convert GitHub markdown to WhatsApp proprietary formatting
            let cleanResponse = response
                .replace(/(\[Agent\]\s*)?Plan execution finished successfully\.?\s*Final Output:?\s*/ig, '')
                .replace(/^Final Output:?\s*/im, '')
                .trim();

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
                console.log(`[Agent] ${cleanResponse.trim()}`);

                // Send result back to WhatsApp with sleek dynamic header
                console.log(`[DEBUG] Attempting to send outbound message to jid: ${replyJid}`);
                const sentMsg = await sock.sendMessage(replyJid, { text: `✨ *${agentName}*\n\n${cleanResponse.trim()}` }).catch(e => {
                    console.error('[DEBUG - WA SEND ERROR]', e);
                    return null;
                });

                if (sentMsg && sentMsg.key?.id) {
                    sentMessageIds.add(sentMsg.key.id!);
                    if (sentMessageIds.size > 1000) sentMessageIds.delete(Array.from(sentMessageIds)[0]!);
                }
            }

            // Clear typing indicator
            await sock.sendPresenceUpdate('paused', replyJid).catch(() => { });

        } catch (error: any) {
            if (composingInterval) clearInterval(composingInterval);
            await sock.sendPresenceUpdate('paused', replyJid).catch(() => { });
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

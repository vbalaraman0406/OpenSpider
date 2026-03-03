import makeWASocket, { DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion, WAMessageStubType, makeCacheableSignalKeyStore } from '@whiskeysockets/baileys';
import * as qrcode from 'qrcode-terminal';
import { Boom } from '@hapi/boom';
import { ManagerAgent } from './agents/ManagerAgent';
import { PersonaShell } from './agents/PersonaShell';
import { logMemory } from './memory';
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import os from 'node:os';

let globalSocket: any = null;
export function getWhatsAppStatus(): 'connected' | 'disconnected' {
    return globalSocket ? 'connected' : 'disconnected';
}
export const sentMessageIds = new Set<string>(); // Global cache for outbound messages to prevent echo loops
// Stores the proto content of sent messages so Baileys can re-relay them on retry requests.
// Without this, getMessage returns undefined and Baileys gives up on retries silently.
const sentMessageStore = new Map<string, any>(); // msgId -> proto message content
const SENT_STORE_MAX = 200;

/**
 * Transcribe audio buffer to text using LOCAL open-source Whisper model.
 * Runs entirely on-device — no API key, no cost, no network calls.
 * Auto-installs ffmpeg and openai-whisper on first use if missing.
 */
async function transcribeAudio(audioBuffer: Buffer, mimetype: string): Promise<string> {
    try {
        // Auto-install ffmpeg if not present (required by Whisper for audio decoding)
        try {
            execSync('which ffmpeg', { stdio: 'ignore' });
        } catch {
            console.log('[WhatsApp] ffmpeg not found — auto-installing via Homebrew...');
            try {
                execSync('brew install ffmpeg', { timeout: 300000, stdio: 'pipe' });
                console.log('[WhatsApp] ✅ ffmpeg installed successfully');
            } catch (brewErr: any) {
                console.error('[WhatsApp] Failed to auto-install ffmpeg:', brewErr.message);
                return '[Voice message received but ffmpeg is not installed. Run: brew install ffmpeg]';
            }
        }

        // Write audio to a temp file
        const ext = mimetype?.includes('ogg') ? 'ogg' : mimetype?.includes('mp4') ? 'mp4' : 'ogg';
        const tmpFile = path.join(os.tmpdir(), `openspider_voice_${Date.now()}.${ext}`);
        fs.writeFileSync(tmpFile, audioBuffer);

        // Whisper model size: "base" is ~150MB, fast, and good for most voice notes.
        // You can change to "small" (~500MB) or "medium" (~1.5GB) for higher accuracy.
        const whisperModel = process.env.WHISPER_MODEL || 'base';

        // Run local Whisper transcription via Python
        // Auto-installs openai-whisper on first use if not present
        const result = execSync(
            `python3 -c "
import sys, json, os
try:
    import whisper
except ImportError:
    print('Installing openai-whisper...', file=sys.stderr)
    os.system('pip3 install -q openai-whisper')
    import whisper

model = whisper.load_model('${whisperModel}')
result = model.transcribe('${tmpFile}')
print(json.dumps({'text': result['text'].strip()}))
"`,
            { timeout: 300000 }  // 5 min timeout for first-run installs + model download
        ).toString().trim();

        // Clean up temp files
        try { fs.unlinkSync(tmpFile); } catch (e) { }

        // Parse the JSON output from the last line
        const lines = result.split('\n');
        const jsonLine = lines[lines.length - 1] || '';
        const parsed = JSON.parse(jsonLine);
        if (parsed.text) {
            console.log(`[WhatsApp] 🎙️ Local Whisper transcription: "${parsed.text}"`);
            return parsed.text;
        }
        return '[Voice message received but transcription returned empty]';
    } catch (err: any) {
        console.error('[WhatsApp] Failed to transcribe audio:', err.message);
        return '[Voice message received but transcription failed]';
    }
}

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
    const result = await globalSocket.sendMessage(jid, { text });
    // Store the sent message so Baileys can re-relay it on retry requests
    if (result?.key?.id && result?.message) {
        sentMessageStore.set(result.key.id, result.message);
        sentMessageIds.add(result.key.id);
        if (sentMessageStore.size > SENT_STORE_MAX) {
            const firstKey = sentMessageStore.keys().next().value;
            if (firstKey) sentMessageStore.delete(firstKey);
        }
    }
}

/**
 * Send an audio/voice message to a WhatsApp JID.
 * Converts input audio (MP3/WAV/etc) to OGG Opus format required by WhatsApp PTT.
 * Sends as a voice note (ptt = push-to-talk) bubble.
 */
export async function sendWhatsAppAudio(jid: string, audioFilePath: string) {
    if (!globalSocket) throw new Error("WhatsApp socket not connected");

    // WhatsApp voice notes REQUIRE audio/ogg; codecs=opus format
    // Convert from MP3/any format to OGG Opus using ffmpeg
    const oggPath = audioFilePath.replace(/\.[^.]+$/, '') + '_wa.ogg';
    try {
        execSync(
            `ffmpeg -y -i "${audioFilePath}" -ac 1 -ar 48000 -c:a libopus -b:a 64k "${oggPath}"`,
            { timeout: 30000, stdio: 'pipe' }
        );
        console.log(`[WhatsApp] Converted audio to OGG Opus: ${oggPath}`);
    } catch (convErr: any) {
        console.error('[WhatsApp] ffmpeg conversion failed, trying raw send:', convErr.message);
        const audioBuffer = fs.readFileSync(audioFilePath);
        await globalSocket.sendMessage(jid, {
            audio: audioBuffer,
            mimetype: 'audio/mpeg',
            ptt: false
        });
        return;
    }

    // Get audio duration in seconds (required for WhatsApp PTT)
    let durationSeconds = 10; // Default fallback
    try {
        const durationStr = execSync(
            `ffprobe -v error -show_entries format=duration -of csv=p=0 "${oggPath}"`,
            { timeout: 5000 }
        ).toString().trim();
        durationSeconds = Math.ceil(parseFloat(durationStr) || 10);
    } catch (e) {
        console.log('[WhatsApp] Could not detect audio duration, using default');
    }

    const audioBuffer = fs.readFileSync(oggPath);
    console.log(`[WhatsApp] 🔊 Sending voice note: ${audioBuffer.length} bytes, ${durationSeconds}s duration to ${jid}`);

    try {
        const result = await globalSocket.sendMessage(jid, {
            audio: audioBuffer,
            mimetype: 'audio/ogg; codecs=opus',
            ptt: true,
            seconds: durationSeconds
        });
        if (result?.key?.id) {
            sentMessageIds.add(result.key.id);
            // Store sent message content for Baileys retry/re-relay on decryption failure
            if (result.message) {
                sentMessageStore.set(result.key.id, result.message);
                if (sentMessageStore.size > SENT_STORE_MAX) {
                    const firstKey = sentMessageStore.keys().next().value;
                    if (firstKey) sentMessageStore.delete(firstKey);
                }
            }
            if (sentMessageIds.size > 1000) {
                const first = Array.from(sentMessageIds)[0];
                if (first) sentMessageIds.delete(first);
            }
        }
        console.log(`[WhatsApp] ✅ Voice note sent, message ID: ${result?.key?.id || 'unknown'}`);
    } catch (sendErr: any) {
        console.error(`[WhatsApp] ❌ Voice note send failed: ${sendErr.message}`);
        // Retry once — Baileys sometimes has transient session issues
        try {
            console.log('[WhatsApp] Retrying voice note send...');
            const retryResult = await globalSocket.sendMessage(jid, {
                audio: audioBuffer,
                mimetype: 'audio/ogg; codecs=opus',
                ptt: true,
                seconds: durationSeconds
            });
            if (retryResult?.key?.id) {
                sentMessageIds.add(retryResult.key.id);
                if (sentMessageIds.size > 1000) {
                    const first = Array.from(sentMessageIds)[0];
                    if (first) sentMessageIds.delete(first);
                }
            }
            console.log('[WhatsApp] ✅ Voice note retry succeeded');
        } catch (retryErr: any) {
            console.error(`[WhatsApp] ❌ Voice note retry also failed: ${retryErr.message}`);
            throw retryErr;
        }
    }

    // Clean up converted file
    try { fs.unlinkSync(oggPath); } catch (e) { }
}

export async function startWhatsApp() {
    // 🧹 Delete stale Signal session files for the bot's own LID before initializing.
    // These files contain the encryption ratchet state from the previous process lifetime.
    // After a restart, the phone has advanced its ratchet but the on-disk session is stale,
    // causing Bad MAC errors on every incoming message. Deleting them forces a fresh handshake.
    try {
        const authDir = path.join(process.cwd(), 'baileys_auth_info');
        if (fs.existsSync(authDir)) {
            const sessionFiles = fs.readdirSync(authDir).filter(f => f.startsWith('session-'));
            let deleted = 0;
            for (const file of sessionFiles) {
                fs.unlinkSync(path.join(authDir, file));
                deleted++;
            }
            if (deleted > 0) console.log(`[WhatsApp] 🧹 Cleared ${deleted} stale Signal session file(s) — fresh sessions will be negotiated`);
        }
    } catch (e: any) {
        console.error('[WhatsApp] Failed to clear stale sessions:', e.message);
    }

    const { state, saveCreds } = await useMultiFileAuthState('baileys_auth_info');
    const manager = new ManagerAgent();

    const { version, isLatest } = await fetchLatestBaileysVersion();
    console.log(`[WhatsApp] Using WA v${version.join('.')}, isLatest: ${isLatest}`);

    const pino = require('pino');
    const NodeCache = require('node-cache');
    const msgRetryCounterCache = new NodeCache();
    const baileysLogger = pino({ level: 'error' });

    const sock = makeWASocket({
        version,
        printQRInTerminal: true,
        auth: {
            creds: state.creds,
            keys: makeCacheableSignalKeyStore(state.keys, baileysLogger)
        },
        logger: baileysLogger,
        markOnlineOnConnect: true,
        syncFullHistory: false,
        msgRetryCounterCache,
        retryRequestDelayMs: 250,
        getMessage: async (key) => {
            // Look up the original sent message content so Baileys can re-relay it on retry.
            // Returning undefined causes Baileys to silently give up on the retry.
            if (key?.id && sentMessageStore.has(key.id)) {
                return sentMessageStore.get(key.id);
            }
            return undefined;
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

            // 🔑 Session Warm-Up: Force Baileys to establish fresh encryption sessions
            // with allowed DM contacts on connection. Presence subscription alone is NOT
            // enough — we need to send actual outbound encrypted packets to force the
            // E2E key exchange and prevent Bad MAC on the first real message.
            setTimeout(async () => {
                try {
                    const configPath = path.join(process.cwd(), 'workspace', 'whatsapp_config.json');
                    if (fs.existsSync(configPath)) {
                        const waConfig = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
                        const dms = waConfig.allowedDMs || [];
                        for (const number of dms) {
                            const cleanNumber = number.replace(/\D/g, '');
                            if (cleanNumber) {
                                const jid = `${cleanNumber}@s.whatsapp.net`;
                                // Subscribe to presence (lightweight)
                                await sock.presenceSubscribe(jid).catch(() => { });
                                // Send 'available' presence TO the contact (forces outbound encryption)
                                await sock.sendPresenceUpdate('available', jid).catch(() => { });
                                // Fetch their profile status (forces another encrypted exchange)
                                await sock.fetchStatus(jid).catch(() => { });
                            }
                        }
                        if (dms.length > 0) {
                            console.log(`[WhatsApp] 🔑 Session warm-up complete: ${dms.length} contact(s) sessions established`);
                        }
                    }
                } catch (e) { }
            }, 3000); // Wait 3s after connection for Baileys internals to settle
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
    const processingMessageIds = new Set<string>(); // In-flight lock to prevent race conditions
    let lastBadMacNotifyTime = 0; // Cooldown timer for Bad MAC ghost notifications

    sock.ev.on('messages.upsert', async (m) => {
        // Only process real-time incoming messages, avoid historical sync appends which cause Double-Messages
        if (m.type !== 'notify') return;

        const msg = m.messages[0];
        if (!msg || typeof msg.key.id !== 'string') return;

        // Message Deduplication Check — two-phase:
        // Phase 1: Check both caches. processingMessageIds = currently in-flight (prevents race conditions)
        // Phase 2: processedMessageIds = fully processed (added after Ghost Trap validation)
        if (processedMessageIds.has(msg.key.id!) || processingMessageIds.has(msg.key.id!)) return;
        // Lock this ID immediately so parallel arrivals of the same msg are blocked
        processingMessageIds.add(msg.key.id!);
        if (processingMessageIds.size > 500) processingMessageIds.delete(Array.from(processingMessageIds)[0]!);

        // We ignore automated broadcasts/status updates
        if (!msg.message || msg.key.remoteJid === 'status@broadcast') {
            processingMessageIds.delete(msg.key.id!);
            return;
        }

        // Ensure we extract text from standard chat, extended chat, or media captions
        let textMessage = msg.message.conversation || msg.message.extendedTextMessage?.text || msg.message.imageMessage?.caption || msg.message.videoMessage?.caption || msg.message.pollCreationMessage?.name || '';

        // Detect voice/audio messages
        const audioMessage = msg.message.audioMessage;
        const isVoiceNote = !!(audioMessage && (audioMessage as any).ptt); // ptt = push-to-talk voice note
        const isAudioFile = !!audioMessage; // Any audio attachment

        // Detect video messages (to inform user)
        const videoMessage = msg.message.videoMessage;

        console.log(`\n[DEBUG - RAW WA MSG] fromMe: ${msg.key.fromMe}, remoteJid: ${msg.key.remoteJid}, text: ${textMessage}`);
        const isGroup = msg.key.remoteJid?.endsWith('@g.us');

        let isNoteToSelf = false;
        // Prevent Infinite Loops without hardcoded signatures:
        // By tracking the exact ID of messages sent by OpenSpider, we can drop echoed bot replies but allow 'Message Yourself' inputs from the human.
        if (msg.key.fromMe) {
            // Check if this was a forwarded message etc
            if (msg.message?.extendedTextMessage?.contextInfo?.isForwarded) {
                processingMessageIds.delete(msg.key.id!);
                return;
            }

            // Strict heuristic perfectly mirroring OpenClaw's design pattern:
            if (sentMessageIds.has(msg.key.id!)) {
                processingMessageIds.delete(msg.key.id!);
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
                processingMessageIds.delete(msg.key.id!);
                return; // Ignore outbound messages sent to other people
            }
        }

        // Handle incoming reactions (just log them for context)
        if (msg.message.reactionMessage) {
            console.log(`[WhatsApp] Received Reaction: ${msg.message.reactionMessage.text} on message ${msg.message.reactionMessage.key?.id}`);
            processingMessageIds.delete(msg.key.id!);
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
        // We require either text, image, audio, or video
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

        // 🎙️ VOICE MESSAGE TRANSCRIPTION
        // If the user sent a voice note or audio file, download and transcribe it to text
        if (isAudioFile && audioMessage) {
            try {
                const { downloadMediaMessage } = await import('@whiskeysockets/baileys');
                const audioBuffer = await downloadMediaMessage(
                    msg,
                    'buffer',
                    {},
                    {
                        logger: console as any,
                        reuploadRequest: sock.updateMediaMessage
                    }
                ) as Buffer;
                const transcription = await transcribeAudio(audioBuffer, (audioMessage as any).mimetype || 'audio/ogg');
                if (transcription && !transcription.startsWith('[Voice message received but')) {
                    textMessage = `[Voice Message] ${transcription}\n\n[SYSTEM: The user sent a voice message. You MUST reply using send_voice tool to send a voice note back. Do NOT reply with text only.]`;
                } else {
                    textMessage = transcription; // Error message passthrough
                }
                console.log(`[WhatsApp] 🎙️ Voice message transcribed: "${textMessage}"`);
            } catch (err: any) {
                console.error('[WhatsApp] Failed to download/transcribe voice message:', err.message);
                textMessage = '[Voice message received but could not be processed]';
            }
        }

        // 🎬 VIDEO MESSAGE NOTIFICATION
        // Inform the user that video processing is not yet supported
        if (videoMessage && !textMessage) {
            textMessage = '[User sent a video message]';
        }

        // 🖼️ IMAGE WITHOUT CAPTION
        // If the user sent an image with no caption, set a fallback text so the message isn't dropped
        if (imageMessage && !textMessage) {
            textMessage = '[User sent an image]';
        }

        // 🔥 BAD MAC / NO SESSION GHOST TRAP 🔥
        // When Signal session is stale or missing, libsignal strips the payload entirely.
        // Silently drop the ghost packet and release the lock — Baileys' msgRetryCounterCache
        // will trigger WhatsApp to re-send with a fresh pre-key bundle automatically.
        if (msg.key.fromMe && !imageMessage && !isAudioFile && textMessage.trim() === '') {
            processingMessageIds.delete(msg.key.id!);
            console.log(`[WhatsApp] 👻 Ghost packet dropped (msg: ${msg.key.id?.slice(-8)}) — waiting for Baileys retry`);
            return;
        }

        if (!textMessage && !imageMessage) {
            // Release lock for any empty message (Bad MAC from other users, etc.)
            processingMessageIds.delete(msg.key.id!);
            return;
        }

        // Now that we verified this is a real, decrypted payload, commit to the permanent cache
        processedMessageIds.add(msg.key.id!);
        if (processedMessageIds.size > 5000) processedMessageIds.delete(Array.from(processedMessageIds)[0]!);
        processingMessageIds.delete(msg.key.id!); // Clean up the in-flight lock

        // --- MESSAGE LOGGING & FIREWALL ---
        console.log(`[You] 📱 (WhatsApp) ${textMessage}`);
        logMemory('User', `📱 (WhatsApp) ${textMessage}`);

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
                logMemory('Agent', cleanResponse.trim());

                // If a voice note was already sent by the Worker, don't send a duplicate text reply
                const lowerResponse = cleanResponse.toLowerCase();
                const mentionsVoice = lowerResponse.includes('voice');
                const mentionsDelivery = lowerResponse.includes('delivered') || lowerResponse.includes('sent') || lowerResponse.includes('elevenlabs');
                const voiceAlreadySent = mentionsVoice && mentionsDelivery;

                if (voiceAlreadySent) {
                    console.log('[WhatsApp] Skipping text reply — voice note was already delivered');
                } else {
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

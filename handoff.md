# OpenSpider Handoff Document

## Session Summary (March 1, 2026)

This session focused heavily on fixing edge cases surrounding WhatsApp's "Message Yourself" feature and the React Dashboard Web UI chat rendering.

### 1. The 503 Service Unavailable Error (Presence Updates)
- **Problem**: When the user texted the bot using their own number ("Message Yourself"), the bot would send a `composing` (typing) presence update back to the sender's JID (`@s.whatsapp.net`). Meta's servers forbid sending presence updates to yourself and instantly crash the connection with a HTTP 503 Service Unavailable stream error.
- **Fix**: We added a strict `isNoteToSelf` check. We ensure that we only send `composing` and `paused` presence updates if the sender is not the bot's own number.

### 2. The "Ghost Payload" (Bad MAC) Decryption Error
- **Problem**: "Message Yourself" packets from linked devices occasionally desync the end-to-end encryption ratchets. `libsignal` throws a "Bad MAC" error and strips the payload, resulting in an empty message hitting the Baileys event listener.
- **Discovery**: We reviewed the legacy `OpenClaw` codebase and discovered that OpenClaw simply dropped these messages silently. In OpenSpider, Baileys' native `msgRetryCounterCache` catches this Bad MAC and securely requests a fresh key from Meta, re-delivering the true payload approximately 2 seconds later.
- **Fix**: We removed the noisy `console.warn` statements about the "Ghost Payload" so the terminal remains clean while the native Baileys retry orchestration happens transparently in the background.

### 3. Web UI Chat Rendering Broken by Logger Formatting
- **Problem**: The user noticed that the React Dashboard Web UI was no longer showing new chat bubbles.
- **Discovery**: We had added `\n` prefixes to the `console.log("[You] ...")` and `console.log("[Agent] ...")` statements in the backend (`whatsapp.ts`) to make terminal logs cleaner. However, the frontend (`App.tsx`) parsed these logs via WebSocket and strictly checked `if (log.data.startsWith('[You]'))`. The leading newlines broke the matcher, causing the frontend to silently drop all chat messages.
- **Fix**: We modified the frontend parser in `dashboard/src/App.tsx` to call `.trim()` on the log data before performing the `startsWith` checks. We also recompiled and deployed the React frontend.

### 4. The Native "Typing..." Bubble for Self-Messages (Current Issue)
- **Problem**: The user strongly preferred seeing the native "typing..." WhatsApp bubble when talking to the bot, *even* when using the "Message Yourself" feature, instead of a custom emoji reaction (⏳).
- **Attempted Fixes**: 
  - We reverted the `replyJid` logic to route outbound messages and presence updates strictly to `msg.key.remoteJid`. For multi-device self-messages, this JID often comes in as an encrypted Device Proxy ID (`...something...@lid`).
  - We attempted a "Fast-Path Composing Trigger" very early in the `whatsapp.ts` `messages.upsert` handler:
    ```typescript
    if (msg.key.fromMe && msg.key.remoteJid) {
        sock.sendPresenceUpdate('composing', msg.key.remoteJid).catch(() => {});
    }
    ```
    This was intended to fire the "typing..." indicator *before* the empty Ghost Payload is dropped by the Bad MAC trap, masking the 2-second decryption retry delay.

## Current Broken State (For the Next Agent)

The user reported two critical failures with the current active build:
1. **Typing Bubble Delay**: The 2-second delay in the typing bubble is *still* happening on self-messages, suggesting the fast-path trigger is failing to reach the device proxy, or Baileys queues presence updates behind decryption retries.
2. **Web UI Regression**: The React Web UI has completely lost all WhatsApp messages again and is not displaying new messages. The frontend parsing logic or WebSocket broadcasting might be broken again.

### Next Steps for the Incoming Agent:
1. Check `pm2 logs openspider-gateway` and verify the `msg.key.remoteJid` for self-messages. Why is the early `sendPresenceUpdate('composing', msg.key.remoteJid)` failing, or is it blocked by the 503 error again?
2. Check `dashboard/src/App.tsx` log filtering logic. Did the recent `.trim()` fix regress, or is the backend no longer dispatching the exact `[You]` and `[Agent]` string structures?
3. Carefully review `whatsapp.ts` line ~190-250. The interplay between `isNoteToSelf`, `@lid` proxies, the Bad MAC return trap, and the presence update is brittle and needs a robust architectural cleanup.

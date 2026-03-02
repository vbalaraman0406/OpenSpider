# Handoff — Session 2026-03-01 (Afternoon)

## Summary
Fixed WhatsApp self-message delivery, native typing bubbles, dashboard chat rendering, and improved the security UI. Two commits pushed to `main`.

---

## Changes Made

### Commit `7d3fde3` — WhatsApp Self-Message Delivery & Dashboard Chat Rendering

#### `src/whatsapp.ts`
- **@lid JID Rerouting**: Self-messages ("Message Yourself") arrive with `remoteJid` as an `@lid` device proxy JID, which is invisible in WhatsApp's chat UI. Outbound replies and presence updates sent to `@lid` are silently blackholed by Meta. Fixed by detecting `@lid` on self-messages and rerouting `replyJid` to `botJid` (`@s.whatsapp.net`).
- **Fast-Path Composing Trigger**: `sendPresenceUpdate('composing')` now fires immediately on message arrival (before the Bad MAC ghost trap). For `@lid` JIDs, composing is rerouted to `@s.whatsapp.net` so the native typing bubble appears in the correct chat window.
- **Resilient Presence Updates**: All `sendPresenceUpdate` calls now use `.catch(() => {})` to prevent Meta 503 rejections from crashing the Baileys connection. Mirrors OpenClaw's error-swallowing pattern.
- **Removed Hourglass Emoji**: Replaced the ⏳ reaction workaround with native composing for all messages (including self-chat).

#### `dashboard/src/App.tsx`
- **Robust Log Matching**: Replaced fragile `.startsWith('[You]')` / `.startsWith('[Agent]')` with `.includes()` to handle log messages with unexpected prefixes or leading whitespace.
- **Fixed Content Extraction**: Uses `substring(indexOf(...))` instead of `.replace()` for precise content parsing.

---

### Commit `be9f41f` — Apply Security Rules Button Visual Feedback

#### `dashboard/src/components/WhatsAppSecurity.tsx`
- **Amber default**: Button is orange/amber to signal an actionable state.
- **Pulsing amber**: Animates during save.
- **Green success**: Turns emerald green with ✓ "Rules Applied!" for 2.5 seconds after successful save, then auto-resets.
- Uses a `saveStatus` state machine (`'idle' | 'saving' | 'saved'`).

---

### Config Fix (not committed — `workspace/` is gitignored)

#### `workspace/whatsapp_config.json`
- Updated `allowedGroups` from placeholder `120363151234567890@g.us` to real group JID `120363423460684848@g.us`.

---

## Key Technical Insights

### @lid vs @s.whatsapp.net
WhatsApp's linked-device architecture uses `@lid` (Linked Identity) proxy JIDs internally. When you send a message to yourself, Baileys often receives it with `remoteJid` as `150457066512456@lid` instead of `14156249639@s.whatsapp.net`. Messages and presence updates sent TO `@lid` JIDs are silently dropped by Meta's servers — they never appear in any chat window. The fix detects `@lid` on self-messages and reroutes to the bot's `@s.whatsapp.net` JID.

### Bad MAC Retry & Ghost Trap
Self-messages trigger Bad MAC errors ~50% of the time due to encryption ratchet de-sync. The first packet arrives with empty text (ghost), gets dropped by the ghost trap. Baileys then renegotiates encryption keys and Meta re-delivers ~2 seconds later with the same message ID. The fast-path composing trigger fires on the ghost packet (which arrives on `@s.whatsapp.net`) so the typing bubble appears immediately — masking the 2-second retry latency.

### PM2 Runs Compiled JS
PM2 executes `dist/index.js`, not `src/index.ts`. Changes to TypeScript source require `npm run build:backend` before `pm2 restart` for changes to take effect.

---

## Known Issues / Open Items

1. **Web UI Live Messages**: WhatsApp messages broadcast via WebSocket do appear live when the dashboard is open, but are NOT persisted to `workspace/memory/*.md` chat history. On page refresh, only memory-persisted messages survive. Consider adding a bridging layer that writes `[You]`/`[Agent]` entries from `whatsapp.ts` into the memory system.

2. **Second Message Typing Bubble Delay**: The first message after a restart shows the typing bubble instantly. Subsequent messages may have a ~2s delay due to the Bad MAC encryption renegotiation. This is a fundamental WhatsApp/libsignal limitation that even OpenClaw experiences.

3. **Group Feature**: Config is set up for group `120363423460684848@g.us` with `botMode: 'mention'`. The bot responds when @mentioned by name ("@Ananta") or tagged via WhatsApp's contact picker. Further group testing needed.

---

## Files Modified This Session

| File | Change |
|------|--------|
| `src/whatsapp.ts` | @lid rerouting, composing trigger, resilient presence |
| `dashboard/src/App.tsx` | `.includes()` log matching |
| `dashboard/src/components/WhatsAppSecurity.tsx` | Save button visual feedback |
| `workspace/whatsapp_config.json` | Correct group JID |

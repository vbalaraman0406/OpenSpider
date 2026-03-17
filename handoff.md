# Agent Handoff — Session 2026-03-16

## 1. Current Goal

Fix WhatsApp group messaging from the bot. The bot can send DMs fine but **cannot send messages to any WhatsApp group** — specifically the "Family" group (`14156249639-1373117853@g.us`). The error is a Baileys Signal protocol issue: `SessionError: No sessions` followed by `not-acceptable` (HTTP 406) on retry.

Secondary goal was improving the **cron job editor's delivery channel picker** in the dashboard — that part is complete and working.

---

## 2. Progress Status

### ✅ Working
- **Contact picker in cron editor**: Groups show first on text search, DMs first on browse. Exact match sorting. Searchable.
- **Delivery channel tag detection**: Group JIDs with hyphens (`14156249639-1373117853@g.us`) now properly detected and shown as 👥 tags.
- **DM tag detection**: `@s.whatsapp.net` patterns detected and shown as 💬 tags.
- **Removable tags**: × buttons correctly strip delivery instructions from the prompt.
- **`/api/whatsapp/send` endpoint**: Fixed to support group JIDs (was always appending `@s.whatsapp.net`).
- **`sendWhatsAppMessage` retry logic**: On "No sessions" error, fetches `groupMetadata()`, calls `assertSessions(participantJids, true)`, waits 2s, retries.
- **DM messaging**: Works perfectly.
- **WhatsApp connection**: Bot connects successfully after QR re-scan (device `:48`).
- **Session warm-up**: 8 contacts, 5 groups warm-up completes on boot.

### ❌ Broken
- **Group messaging**: ALL group sends fail. Tested Family group (`14156249639-1373117853@g.us`) extensively. Error flow:
  1. First attempt: `SessionError: No sessions` at `libsignal/session_cipher.js:71`
  2. `assertSessions(16 participants, force=true)` runs successfully
  3. Retry attempt: `not-acceptable` (HTTP 406) from WhatsApp server
  4. The failing participant is the **bot's own LID** (`150457066512456.0`) — a self-session issue during sender key distribution
- **QR re-scan did NOT fix it**: Fresh `baileys_auth_info` (deleted and re-scanned), device changed from `:47` to `:48`, but same error persists.

### Root Cause Analysis
The error at `Object.150457066512456.0` (bot's own LID) in `session_cipher.js:171` means the bot cannot establish a Signal sender key session with **itself** in the group. This is likely a **Baileys 6.17.16 bug** with LID-based group messaging. Baileys 7.0.0-rc.9 is available and may fix this.

---

## 3. Active Context — Files Edited

| File | What Changed |
|------|-------------|
| `dashboard/src/App.tsx` | Contact picker dropdown (lines ~1727-1810): dynamic ordering (groups first on text search), group JID regex fixed to support hyphens `[\d-]+@g.us` |
| `src/whatsapp.ts` | `sendWhatsAppMessage()` (lines ~280-330): retry logic with `assertSessions` + `groupMetadata` on "No sessions" error |
| `src/server.ts` | `/api/whatsapp/send` endpoint (line ~692): fixed JID handling — `to.includes('@') ? to : ${to}@s.whatsapp.net` |

---

## 4. All Features Delivered This Session

1. **Cron job WhatsApp contact picker** — searchable dropdown with groups + DMs when editing a cron job
2. **Dynamic dropdown ordering** — text search shows groups first, number/empty search shows DMs first
3. **Group JID tag detection** — hyphenated JIDs like `14156249639-1373117853@g.us` correctly detected in prompt
4. **Exact-match group sorting** — searching "Family" shows exact "Family" match before "Morsbach family"
5. **Removable delivery channel tags** — 👥 groups, 💬 DMs, 📧 emails with × remove buttons
6. **`/api/whatsapp/send` fix** — now supports group JIDs directly (was broken for groups)
7. **`sendWhatsAppMessage` retry** — `assertSessions` + `groupMetadata` refresh on "No sessions" errors
8. **Cron logs persistence** — logs survive dashboard refresh (from earlier in session)

---

## 5. Next Immediate Steps

### Option A: Upgrade Baileys (Recommended)
The group messaging issue is almost certainly a Baileys 6.x LID bug. Version 7.0.0-rc.9 exists.

- [ ] Check Baileys 7.x changelog for LID/group fixes: `npm view @whiskeysockets/baileys versions --json`
- [ ] Back up current `node_modules/@whiskeysockets/baileys` 
- [ ] Run `npm install @whiskeysockets/baileys@latest`
- [ ] Check for breaking API changes in `makeWASocket`, `sendMessage`, `groupFetchAllParticipating`
- [ ] Delete `baileys_auth_info` and re-scan QR: `openspider channels login`
- [ ] Build and test: `npm run build && pm2 restart openspider-gateway`
- [ ] Test group send: `curl -X POST -H "X-API-Key: $KEY" -H "Content-Type: application/json" -d '{"to":"14156249639-1373117853@g.us","text":"test"}' http://localhost:4001/api/whatsapp/send`

### Option B: Workaround (If upgrade is too risky)
- [ ] Investigate if the bot's own LID can be excluded from `assertSessions` participant list
- [ ] Try sending with `{ cachedGroupMetadata: undefined }` in socket config
- [ ] Check if `sock.sendMessage(jid, { text }, { participant: { jid: botLid } })` options can skip self-encryption
- [ ] Try downgrading to Baileys `6.16.x` if the issue is a regression in `6.17.16`

### Git Status
- All changes committed and pushed to `main`
- Latest commit: `0ab0ad6` — "fix: group JID regex to support hyphenated JIDs"
- The `/api/whatsapp/send` fix (server.ts) needs to be committed: `git add src/server.ts && git commit -m "fix: /api/whatsapp/send now supports group JIDs" && git push`

# OpenSpider Agent Handoff — Session Context

> **Date:** 2026-03-10  
> **Version:** v2.2.0  
> **Last Tag:** `v2.1.0-stable` (rollback point)  
> **Gateway Status:** Running via `pm2` (openspider-gateway)

---

## 1. Current State

All v2.2.0 features have been implemented, built, and deployed. The gateway has been restarted with the new code.

---

## 2. Version History

### v2.2.0 — LID Dashboard, Email Config, CLI (Current)

#### A. LID Mapping Dashboard UI
- **LID Identity Mappings** panel in WhatsApp Security (Channels → Configure WhatsApp)
- When an unknown LID tries to DM, it appears as a **pending amber card** with the LID pre-filled
- User types the phone number and clicks "Map" — no need to know the LID number
- Resolved mappings are shown below with delete buttons
- Backed by `GET /api/whatsapp/lid-mappings`, `GET /api/whatsapp/lid-pending`, `DELETE /api/whatsapp/lid-map/:lid`

#### B. Email Configuration
- **Email Notification Settings** panel in Channels → Configure WhatsApp
- Two configurable fields:
  - **Cron Job Results To:** — where automated cron results are delivered
  - **Vendor & Friends To:** — default outbound email recipient
- Stored in `workspace/email_config.json`
- Backed by `GET /api/email/config`, `POST /api/email/config`

#### C. Persisted `lidNotifiedCache`
- The notification dedup cache (tracks which LIDs have been admin-notified) now persists to `workspace/lid_notified_cache.json`
- Survives gateway restarts — blocked LIDs won't re-notify the admin
- Debounce-written every 2 seconds

#### D. CLI `openspider lid-map`
- New command: `openspider lid-map <LID> <PHONE>`
- Maps a WhatsApp LID to a phone number via the running gateway API
- Reads PORT and DASHBOARD_API_KEY from `.env` for authentication

#### E. Version Bump
- `package.json`: `2.2.0`
- CLI `.version()`: `2.2.0`

### v2.1.0 — Memory & Context Optimization Suite
1. Global Context Compaction — Worker results capped at 600 chars
2. Smart Persona Context — Only LLM-relevant fields sent
3. Skill Lazy Loading — Compact skill list
4. End-of-Day Compaction — `compactYesterdayLog()`
5. Memory Retention Policy — `cleanupOldMemoryLogs(30)`
6. Channel-Tagged Memory — 📱/🖥️/⏰ tags

### v2.0.x — LID Resolution System
- LID↔Phone Cache — Persistent `lid_cache.json` + in-memory Maps
- Admin `map` command — WhatsApp-based LID mapping
- Admin Notifications — Blocked LID alerts with `map` syntax
- Bot LID in Mention Checks — Group + DM mention checks match bot's `myLid`
- POST /api/whatsapp/lid-map — API endpoint for LID mapping

---

## 3. Active Files (v2.2.0)

| File | What Changed |
|------|-------------|
| `src/whatsapp.ts` | Persisted `lidNotifiedCache` to disk, added `getLidMappings()`, `removeLidMapping()`, `getPendingLids()` exports |
| `src/server.ts` | Added 5 endpoints: `GET /api/whatsapp/lid-mappings`, `GET /api/whatsapp/lid-pending`, `DELETE /api/whatsapp/lid-map/:lid`, `GET /api/email/config`, `POST /api/email/config` |
| `src/cli.ts` | Added `openspider lid-map <LID> <PHONE>` command, version bumped to `2.2.0` |
| `dashboard/src/components/WhatsAppSecurity.tsx` | Added `LidMappingsPanel` with pending LIDs + resolved mappings |
| `dashboard/src/components/EmailSettings.tsx` | **New file.** Email notification settings panel |
| `dashboard/src/App.tsx` | Imported and rendered `<EmailSettings />` |
| `package.json` | Version `2.2.0` |

---

## 4. Key Architecture Notes

### LID Resolution Flow (DM Firewall)
```
Incoming DM from @lid JID
  │
  ├── Direct Match: phone number in allowlist → ✅ (normal @s.whatsapp.net)
  ├── Layer 1: LID cache lookup (lid_cache.json) → ✅ if cached
  ├── Layer 2: Config lid field match (whatsapp_config.json entry.lid) → ✅
  ├── Layer 3: Group participant scan (cross-ref LID in groups) → ✅ if found
  └── Layer 4: BLOCK + admin notification with "map <LID> <PHONE>" 
```

### Important Variables in `whatsapp.ts`
- `lidPhoneCache: Map<string, string>` — LID → phone (in-memory)
- `phoneLidCache: Map<string, string>` — phone → LID (in-memory, reverse)
- `lidNotifiedCache: Set<string>` — tracks notified LIDs (**persisted to disk**)
- `myLid: string` — bot's own LID JID (discovered on connection/creds update)

### Workspace Config Files
- `workspace/whatsapp_config.json` — DM/group allowlist, policies, LID fields on entries
- `workspace/lid_cache.json` — LID↔phone mappings
- `workspace/lid_notified_cache.json` — LIDs already admin-notified (dedup)
- `workspace/email_config.json` — Email notification settings (`cronResultsTo`, `vendorEmailTo`)

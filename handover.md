# Session Handover — March 2, 2026

## Summary

Major reliability and feature improvements across the OpenSpider codebase: chat history persistence, WhatsApp self-message detection, cron scheduler upgrade, agent system knowledge, workspace defaults for fresh installs, and comprehensive documentation updates.

---

## Changes Made (Chronological)

### 1. Group Chat Agent Introduction (`whatsapp.ts`, `SOUL.md`)
- Updated `SOUL.md` with "Group Chat Behavior" section — agent introduces itself with `@Ananta <msg>` format in groups
- Updated `whatsapp.ts` to prepend `[GROUP CHAT]` tag with agent name to the manager prompt for group messages

### 2. Explicit Self-Introduction Rules (`SOUL.md`)
- Made SOUL.md instruction explicit about which IDENTITY.md fields to include (CEO/Boss, Company, Website, etc.)
- Previously the LLM was cherry-picking which fields to mention and skipping CEO/Boss/Company

### 3. WhatsApp Note-to-Self Fix (`whatsapp.ts`)
- **Bug**: `isNoteToSelf` used `remoteJid?.includes('@lid')` which matched ALL linked-device outbound messages — every message sent to anyone triggered the AI
- **Fix**: Changed to only match the bot's own number via `remoteJid?.startsWith(botNumber)` and the bot's own LID via `sock.user.lid`
- Restored "Message Yourself" functionality using bot's own LID instead of any `@lid`

### 4. Plan Execution Output Stripping (`App.tsx`)
- Added regex to strip `Plan execution finished successfully. Final Output:` from agent responses in the chat UI
- Users no longer see internal system messages in the chat view

### 5. Dashboard Chat History Persistence (`server.ts`, `whatsapp.ts`)
**Root cause**: Two issues — WhatsApp messages never saved to memory files, and WebSocket events were fire-and-forget with no buffer.

**Three-layer fix**:
| Layer | What | File |
|-------|------|------|
| Server Event Buffer | Last 500 chat events stored in memory, replayed to new WebSocket connections | `server.ts` |
| Chat Response Buffering | Agent responses also buffered alongside log events | `server.ts` |
| WhatsApp Memory Logging | Both user messages and agent responses now call `logMemory()` | `whatsapp.ts` |

### 6. Cron Scheduler Upgrade (`scheduler.ts`, `cron_jobs.json`, `App.tsx`, `server.ts`)
- **New feature**: `preferredTime` field for time-of-day scheduling (e.g., `"07:00"` for daily 7 AM)
- Uses 5-minute window matching + same-day dedup to prevent double-triggering
- Interval-based jobs continue working as before
- Weather job set to daily at 7:00 AM, Iran job changed to every 1 hour
- Dashboard UI updated with time picker in "Deploy Job" modal
- Server cron API updated to accept `preferredTime`

### 7. System Architecture Knowledge (`SOUL.md`)
- Added "System Architecture Knowledge" section telling the agent where files live:
  - `workspace/cron_jobs.json` — cron jobs
  - `workspace/memory/YYYY-MM-DD.md` — conversation logs
  - `workspace/agents/<id>/` — agent configs
  - `workspace/whatsapp_config.json` — WhatsApp policies
  - `skills/` — custom tools
- Agent was previously guessing wrong filenames when asked about system status

### 8. Workspace Defaults for Fresh Installs (`workspace-defaults/`, `memory.ts`)
- Created `workspace-defaults/` template directory with all default agent configs (manager, coder, researcher)
- Updated `initWorkspace()` to detect first run and copy defaults → `workspace/`
- `.gitignore` keeps `workspace/` blanket-ignored (sensitive data protection) while `workspace-defaults/` is tracked
- Default manager IDENTITY.md has placeholder fields for new users to customize

### 9. Documentation Overhaul (`docs/`, `README.md`)
- **New page**: `docs/agents.md` — comprehensive agent customization guide (pillar files, defaults, creating agents)
- **Updated**: `docs/configuration.md` — `preferredTime` cron field, time-of-day scheduling, workspace-defaults section
- **Updated**: `docs/architecture.md` — scheduling modes table, workspace first-run seeding
- **Updated**: `docs/.vitepress/config.mts` — added Agent Configuration to nav/sidebar
- **Rewritten**: `README.md` — features, quick start, project structure, agent config, cron scheduling, LLM providers
- **Deployed**: VitePress docs site rebuilt and deployed to Google App Engine (`vish-cloud.wl.r.appspot.com`)

---

## Key File Changes

| File | Type | What Changed |
|------|------|-------------|
| `src/server.ts` | Modified | Event buffer (500 events), chat response buffering, cron API `preferredTime` |
| `src/whatsapp.ts` | Modified | Note-to-self fix, `logMemory()` calls for WhatsApp messages |
| `src/scheduler.ts` | Rewritten | Time-of-day scheduling via `preferredTime`, interval + time-of-day modes |
| `src/memory.ts` | Modified | `initWorkspace()` seeds from `workspace-defaults/` on first run |
| `dashboard/src/App.tsx` | Modified | Plan output stripping, cron `preferredTime` UI, time picker |
| `workspace/agents/manager/SOUL.md` | Modified | System architecture knowledge, self-intro rules, group chat behavior |
| `workspace/cron_jobs.json` | Modified | Weather → 7:00 AM daily, Iran → every 1 hour |
| `workspace-defaults/` | **New** | Template directory for fresh installs (all 3 agent pillar files) |
| `docs/agents.md` | **New** | Agent configuration documentation page |
| `docs/configuration.md` | Modified | `preferredTime`, workspace defaults |
| `docs/architecture.md` | Modified | Scheduling modes, first-run seeding |
| `README.md` | Rewritten | Comprehensive project overview |
| `.gitignore` | Modified | Comment clarifying workspace-defaults is tracked |

---

## Current System State

- **PM2**: Running (`openspider-gateway`, restart count 34)
- **Port**: 4001
- **Docs site**: Deployed at `https://vish-cloud.wl.r.appspot.com`
- **Cron jobs**: 2 active — Weather daily at 7:00 AM, Iran War every 1 hour
- **Git**: All changes pushed to `main` branch on GitHub

## Known Issues / Future Work

- VitePress `printQRInTerminal` deprecation warnings in PM2 logs (cosmetic, from Baileys)
- Dashboard `App.tsx` is ~2050 lines — could benefit from component extraction
- No automated tests yet
- `workspace-defaults/` only seeds on true first run (no `workspace/` dir) — consider a version check for upgrades

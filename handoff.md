# OpenSpider — Session Handoff (March 2, 2026)

## Version: 2.0.1

All changes committed and pushed to `main`. Doc site deployed to Google App Engine.

---

## 2. Security Hardening (v2.0.1)

A full application security audit was conducted. All **Critical** and **High** vulnerabilities were remediated.

### CRIT-1: API Authentication Middleware
- Created `src/middleware/auth.ts` with `apiKeyAuth()` Express middleware and `validateWsConnection()` for WebSocket auth
- All `/api/*` routes now require `X-API-Key` header (except `/api/health` which remains public)
- WebSocket connections validated via `?apiKey=` query param
- CORS locked to `localhost` / `127.0.0.1` only (was open `*`)
- `DASHBOARD_API_KEY` added to `.env` (64-char auto-generated hex key)
- Dashboard frontend updated: `apiFetch()` helper in `dashboard/src/lib/apiFetch.ts` attaches key to all API calls

### CRIT-2: Shell Injection Fixed
- `src/agents/WorkerAgent.ts`: `send_email` and `send_voice` replaced `execSync` template strings with `spawnSync` argument arrays — arguments never pass through the shell

### HIGH-4: Path Traversal Fixed
- `src/server.ts`: `PUT /api/agents/:id` and `POST /api/agents/:id/skills` now use `path.resolve()` + `startsWith()` traversal guard

### HIGH-3: Hardcoded Webhook Token Removed
- `src/webhooks/gmail.ts`: Removed `|| 'OPENSPIDER_HOOK_TOKEN'` fallback; now returns 403 if env var not set or too short
- `OPENSPIDER_HOOK_TOKEN` added to `.env` (auto-generated)

### HIGH-1: Command Sandbox Hardened
- `src/tools/DynamicExecutor.ts`: Added shell metacharacter detection (`; | & \` $ () <>`), replaced string blocklist with regex patterns catching `chmod` variants, `curl|bash`, `nc`, `cat /etc` etc.

### HIGH-2: Script Threat Scanner Expanded
- `src/tools/DynamicExecutor.ts`: Added `importlib`, `__import__`, `getattr`, `socket.`, `urllib.request` bypass patterns
- `writeScript()` and `executeScript()` now use `path.basename()` + traversal guard on filenames

### HIGH-5: File Upload Hardened
- `src/server.ts`: 10MB per-file limit, leading-dot stripping, path traversal guard on uploaded filenames

**All 10 regression tests pass. Backend and frontend build clean.**

---

## 1. Bad MAC / Encryption Fixes

**Problem:** After every restart, the first message (and sometimes subsequent ones) failed with `Bad MAC` errors due to stale WhatsApp Signal encryption sessions.

**Root cause:** OpenSpider wasn't using `makeCacheableSignalKeyStore` like the working OpenClaw implementation, and stale `session-*.json` files persisted across restarts.

**Files modified:** `src/whatsapp.ts`

### Fixes applied:
1. **`makeCacheableSignalKeyStore`** — Wrapped `state.keys` in the Baileys socket config for proper session renegotiation
2. **Stale session cleanup** — On startup, all `session-*.json` files in `baileys_auth_info/` are deleted (preserves `creds.json` pairing)
3. **`sentMessageStore`** — New `Map` caching outgoing message proto content so `getMessage` callback can return it for Baileys retry re-relay
4. **`getMessage` callback** — Returns stored message from `sentMessageStore` if found, otherwise `undefined` (signals Baileys to request retry from WhatsApp servers)
5. **Processing lock leak fix** — Added `processingMessageIds.delete(msg.key.id!)` before ALL 5 early-return paths:
   - `status@broadcast` messages
   - Forwarded messages
   - `sentMessageIds` echo suppression
   - `!isNoteToSelf` check
   - Reaction messages
6. **Ghost packet handling** — Bad MAC ghost packets (empty `fromMe` messages) are silently logged; user notification removed

---

## 2. Voice Message Fixes

**Problem:** Duplicate voice messages sent; text reply alongside voice reply.

**Files modified:** `src/whatsapp.ts`, `workspace/agents/manager/IDENTITY.md`

### Fixes applied:
1. **Single-task rule** — Manager's system prompt requires exactly one task for voice replies
2. **Voice reply suppression** — Keyword-based detection (`send_voice`, `voice note sent`) prevents duplicate text replies when a voice note is sent
3. **Sent message store for voice** — Voice note proto content stored in `sentMessageStore` for retry support

---

## 3. Dashboard UI Upgrade (v2.0.0)

### Version Badge
- Bumped `package.json` to `2.0.0`
- `v2.0.0` pill badge displayed next to "OpenSpider" logo in sidebar
- Fetched live from `/api/health` endpoint

### Theme Toggle (Dark / Light / System)
- **CSS custom properties** in `dashboard/src/index.css` with `[data-theme]` attribute
- Light mode overrides all `slate-950/900/800` Tailwind classes via CSS specificity
- System mode follows OS `prefers-color-scheme`
- Persisted in `localStorage` as `openspider-theme`
- 3-way toggle (☀️ Light / 🌙 Dark / 💻 Auto) in sidebar bottom

### Health Status Indicator
- **Backend:** New `GET /api/health` endpoint in `src/server.ts` returns:
  - `version`, `status` (green/amber/red), `uptime`, `memory` (MB)
  - `components`: whatsapp, llm, server, scheduler
- **Frontend:** New `getWhatsAppStatus()` export in `src/whatsapp.ts`
- Green pulsing heart = all healthy
- Amber = degraded (WhatsApp disconnected or memory >1GB)
- Red = server unreachable
- Hover tooltip shows detailed component status, memory, uptime
- Auto-polls every 30 seconds

### Files modified:
| File | Changes |
|---|---|
| `package.json` | Version bump to 2.0.0 |
| `src/server.ts` | Added `/api/health` endpoint |
| `src/whatsapp.ts` | Added `getWhatsAppStatus()` export |
| `dashboard/src/index.css` | Full theme system with CSS custom properties |
| `dashboard/src/App.tsx` | Theme state/toggle, health state/widget, version badge, Lucide icons (Sun, Moon, Monitor, Heart) |

---

## 4. Documentation Update & Deployment

**Site:** VitePress at `docs/` → deployed to Google App Engine at **https://vish-cloud.wl.r.appspot.com**

### Pages updated:
| Page | Changes |
|---|---|
| `docs/index.md` | v2.0.0 hero, voice/theme/health feature cards, updated capabilities table |
| `docs/dashboard.md` | Version badge, theme toggle, health indicator, file attachments, cron results, API endpoints reference, process monitor |
| `docs/voice.md` | **NEW** — Voice-in (Whisper), voice-out (ElevenLabs), config, dependencies, troubleshooting |
| `docs/channels.md` | Voice messages section, Signal session management |
| `docs/troubleshooting.md` | Bad MAC errors, intermittent message drops, voice notes troubleshooting |
| `docs/.vitepress/config.mts` | Voice Messages in nav/sidebar, site title → "OpenSpider v2.0" |

---

## 5. Git Commits (this session)

| Commit | Description |
|---|---|
| `5fa5ce3b` | fix: resolve Bad MAC, duplicate voice, and intermittent message drops |
| `52f7b8fa` | feat(dashboard): add version badge v2.0.0, theme toggle, and health status indicator |
| `c5263a67` | docs: update all documentation for v2.0.0 features |

---

## 6. Architecture Quick Reference

```
OpenSpider/
├── src/
│   ├── whatsapp.ts          # Baileys socket, message handling, voice, encryption
│   ├── server.ts            # Express + WebSocket server, API endpoints
│   ├── agents/              # ManagerAgent, WorkerAgent
│   └── llm/providers/       # Gemini, Anthropic, OpenAI, Ollama, Custom
├── dashboard/
│   ├── src/App.tsx           # Main React app (~2300 lines)
│   ├── src/index.css         # Theme system (CSS custom properties)
│   └── src/components/       # WhatsAppSecurity, VoiceSettings, AgentFlowGraph, UsageView
├── docs/                     # VitePress documentation site
│   ├── app.yaml              # Google App Engine config
│   └── .vitepress/config.mts # Site navigation
├── workspace/                # Runtime agent configs, memory, cron jobs
└── baileys_auth_info/        # WhatsApp auth (creds.json + session files)
```

## 7. Key Environment Variables

| Variable | Purpose |
|---|---|
| `DEFAULT_PROVIDER` | LLM provider (antigravity, anthropic, openai, ollama, custom) |
| `GEMINI_API_KEY` | Google Gemini API key |
| `ENABLE_WHATSAPP` | Enable WhatsApp channel |

Voice config is in `voice_config.json` (ElevenLabs API key, voice name, model).

## 8. Running Locally

```bash
# Build
npm run build:backend && npm run build:frontend

# Start (PM2 daemon)
openspider start
# or: pm2 restart all

# Dashboard
open http://localhost:4001

# Docs dev
cd docs && npm run docs:dev

# Deploy docs
cd docs && npm run docs:build && gcloud app deploy --quiet
```

## 9. Known Issues / Watch Items

1. **Terminal shell freezes** — The agent's terminal sometimes freezes and can't execute commands. User may need to run commands manually.
2. **Baileys updates** — Monitor for Baileys library updates that may change encryption behavior.
3. **Memory usage** — Health endpoint flags >1GB as amber. Monitor for memory leaks with long-running sessions.
4. **Light theme coverage** — CSS overrides cover the main classes but some deeply nested components (modals, tooltips) may need additional light theme rules if they look off.

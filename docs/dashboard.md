# Dashboard

OpenSpider includes a real-time web dashboard built with **React** and **Vite**, served directly by the Express server on port 4001.

## Accessing the Dashboard

```bash
openspider dashboard
```

Or navigate to [http://localhost:4001](http://localhost:4001) in your browser.

## Version Badge

The dashboard displays the current OpenSpider version (e.g. **v2.2.0**) next to the logo in the sidebar. The version is fetched live from the `/api/health` endpoint and reflects what's in `package.json`.

## Theme Toggle 🎨

The sidebar includes a **3-way theme toggle** at the bottom:

| Mode | Icon | Behavior |
|---|---|---|
| **Light** | ☀️ | Light backgrounds, dark text |
| **Dark** | 🌙 | Dark backgrounds, light text (default) |
| **Auto** | 💻 | Follows your OS `prefers-color-scheme` setting |

The selected theme is persisted in `localStorage` and applied instantly via CSS custom properties.

## Health Status Indicator 💚

A real-time health indicator at the bottom of the sidebar shows system health at a glance:

| Status | Color | Meaning |
|---|---|---|
| 🟢 **Healthy** | Green | All systems operational |
| 🟡 **Degraded** | Amber | Some components unavailable (e.g. WhatsApp disconnected) |
| 🔴 **Unreachable** | Red | Server not responding |

**Hover** over the health indicator to see detailed component status:
- WhatsApp connection status
- LLM provider name
- Server status
- Memory usage (MB)
- Uptime duration

The indicator auto-polls `/api/health` every 30 seconds.

## Dashboard Tabs

### Agent Chat 💬

A full chat interface for communicating directly with your agents.

**Features:**
- Send messages and see agent responses in real-time via WebSocket
- **File attachments** — Click the 📎 paperclip to attach images, documents, or any file
- **Input history** — Press `↑`/`↓` arrow keys to recall previous messages
- **Agent emoji avatars** — Each agent displays its role emoji (🧠 Manager, ⚡ Coder, 🔮 Researcher)
- **Cron job results** — Scheduled task outputs display inline with a ⏰ Cron badge
- **Verbose/Non-verbose toggle** — Switch between raw logs and clean chat bubbles
- Messages show which agent responded with timestamps (visible on hover)

### Agent Flow 🔀

A live visualization of the Manager→Worker delegation flow using Mermaid-based graphs.

**Features:**
- Nodes represent agents with role-specific emojis
- **Instruction labels** on edges show what the Manager delegated
- **Result nodes** appear after task completion with result snippets
- Updates in real-time as agents work

### System Logs 📋

A comprehensive log viewer with filtering, search, and export.

**Features:**
- **Level filtering** — Toggle Trace, Debug, Info, Warn, Error independently
- **Level counts** — Each button shows the count (e.g., `TRACE 78`)
- **Content classification** — Logs auto-classified by keywords (error/failed → Error, warn/⚠ → Warn)
- **Search** — Real-time text search across all logs
- **Download** — Export filtered logs as a `.log` file
- **Auto-follow** — Checkbox to auto-scroll to newest logs
- **Color-coded** — Left border and level badge colored by severity

### Agent Workspace 📁

Manage your AI team directly from the UI without touching the core filesystem.

**Features:**
- **Create Agents** — Click "Create Agent" to bootstrap a new agent persona.
- **Rename Agents** — Select an agent and edit the `name` field in the CAPABILITIES tab to gracefully change its display name.
- **Modify Personas** — Edit the `IDENTITY` and `SOUL` tabs to tweak behavior, vibe, and safety guardrails in real-time.
- **Teach User Context** — Update the `USER CONTEXT` tab to persist your preferences or background so the agent remembers.
- **Manage Skills & Models** — Use the `CAPABILITIES` tab to add/remove tools or switch the underlying LLM processing the agent's thought loop.
- **Instant Persistence** — Click **Save Changes** to immediately sync your UI edits out to the agent's pillar files (`IDENTITY.md`, `SOUL.md`, etc.).

### Dynamic Skills ⚙️

View metadata for available agent skills:
- `browse_web` — Web browsing via Playwright
- `schedule_task` — Create cron jobs
- `wait_for_user` — Pause for user input
- Custom skills can be added via skill metadata files in `skills/`

### Usage Analytics 📊

Track token usage, API calls, and costs across providers and models.

### WhatsApp Security 🔒

Visual interface for managing WhatsApp access controls:

- **DM Allowlist** — Add/remove permitted phone numbers
- **Group Allowlist** — Add/remove permitted groups
- **Per-group mode toggles** — Switch each group between Mention and Listen mode
- **LID Identity Mappings** — View pending blocked LIDs and assign phone numbers. When an unknown LID tries to DM, it appears here as a pending amber card. Type the phone number and click "Map" to allow access. Resolved mappings are listed with delete buttons.
- **Voice Settings** — Configure ElevenLabs voice responses (see [Voice Messages](/voice))
- **Email Notification Settings** — Configure email recipients:
  - **Cron Job Results To** — Email address where automated cron job results are delivered
  - **Vendor & Friends To** — Default email address for outbound emails to vendors/contacts
- Changes save directly to `workspace/whatsapp_config.json` and `workspace/email_config.json`

### Cron Jobs ⏰

Manage scheduled tasks:
- View all configured cron jobs with descriptions and intervals
- Enable/disable individual jobs
- Manually trigger a job for immediate execution
- Monitor last run timestamps
- Cron results appear inline in the Agent Chat view

### Process Monitor 🖥️

Monitor running system processes and resource usage.

### Overview 📈

A high-level summary view of your OpenSpider instance.

### Sessions 📋

View and manage active agent sessions.

## Favicon & PWA Icon

The dashboard includes a full favicon suite for crisp display across all platforms:

| File | Size | Used for |
|---|---|---|
| `favicon-16.png` | 16×16 | Browser tab icon |
| `favicon-32.png` | 32×32 | High-DPI browser tabs |
| `favicon-192.png` | 192×192 | Android home screen |
| `favicon-512.png` | 512×512 | PWA splash screen |
| `apple-touch-icon.png` | 180×180 | iOS home screen bookmark |

The browser chrome (address bar on Android/Chrome) uses `#0f172a` as the theme color, matching the dark navy dashboard background.

::: tip
If the favicon doesn't update after redeployment, do a hard refresh: **Cmd+Shift+R** (Mac) or **Ctrl+Shift+R** (Windows). Browsers cache favicons aggressively.
:::

## Architecture

The dashboard is a single-page React application:

| Component | File | Description |
|---|---|---|
| Main App | `dashboard/src/App.tsx` | All tabs and views (~2450 lines) |
| WhatsApp Security | `dashboard/src/components/WhatsAppSecurity.tsx` | Channel config + LID mapping UI |
| Email Settings | `dashboard/src/components/EmailSettings.tsx` | Email notification config |
| Voice Settings | `dashboard/src/components/VoiceSettings.tsx` | ElevenLabs voice config |
| Agent Flow Graph | `dashboard/src/components/AgentFlowGraph.tsx` | Mermaid flow visualization |
| Usage View | `dashboard/src/components/UsageView.tsx` | Token usage analytics |

### Real-time Updates

The dashboard connects to the server via WebSocket for:
- Agent chat messages
- Agent flow events (task_start, task_complete)
- System log streaming
- Chat response notifications (typing indicators)

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | System health, version, uptime, component status |
| `/api/config` | GET | Current LLM provider and connection status |
| `/api/chat/history` | GET | Chat message history |
| `/api/agents` | GET | Agent configurations |
| `/api/skills` | GET | Available skills |
| `/api/usage` | GET | Token usage data |
| `/api/cron` | GET | Cron job configurations |
| `/api/processes` | GET | Running processes |
| `/api/whatsapp/config` | GET | WhatsApp security config |
| `/api/whatsapp/lid-mappings` | GET | All LID→phone mappings |
| `/api/whatsapp/lid-pending` | GET | Unmapped pending LIDs |
| `/api/whatsapp/lid-map` | POST | Add a LID→phone mapping |
| `/api/whatsapp/lid-map/:lid` | DELETE | Remove a LID mapping |
| `/api/email/config` | GET | Email notification settings |
| `/api/email/config` | POST | Save email notification settings |
| `/api/voice/config` | GET | Voice response config |

### Build & Serve

In **production**, the dashboard is pre-built and served as static files:

```bash
cd dashboard && npm run build    # Builds to dashboard/dist/
```

The Express server serves `dashboard/dist/` automatically.

In **development**, run the Vite dev server with hot-reload:

```bash
cd dashboard && npm run dev      # Usually http://localhost:5173
```

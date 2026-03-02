# Dashboard

OpenSpider includes a real-time web dashboard built with **React** and **Vite**, served directly by the Express server on port 4001.

## Accessing the Dashboard

```bash
openspider dashboard
```

Or navigate to [http://localhost:4001](http://localhost:4001) in your browser.

## Dashboard Tabs

### Agent Chat 💬

A chat interface for communicating directly with your agents.

**Features:**
- Send messages and see agent responses in real-time via WebSocket
- **Input history** — Press `↑`/`↓` arrow keys to recall previous messages
- **Agent emoji avatars** — Each agent displays its role emoji (🧠 Manager, ⚡ Coder, 🔮 Researcher)
- Messages show which agent responded with timestamps

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

Browse the `workspace/` directory structure, view agent configuration files, and inspect persona settings.

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
- Changes save directly to `workspace/whatsapp_config.json`

### Cron Jobs ⏰

Manage scheduled tasks:
- View all configured cron jobs with descriptions and intervals
- Enable/disable individual jobs
- Manually trigger a job for immediate execution
- Monitor last run timestamps

## Architecture

The dashboard is a single-page React application:

| Component | File | Description |
|---|---|---|
| Main App | `dashboard/src/App.tsx` | All tabs and views (~2050 lines) |
| WhatsApp Security | `dashboard/src/components/WhatsAppSecurity.tsx` | Channel config UI |
| Agent Flow Graph | `dashboard/src/components/AgentFlowGraph.tsx` | Mermaid flow visualization |
| Usage View | `dashboard/src/components/UsageView.tsx` | Token usage analytics |

### Real-time Updates

The dashboard connects to the server via WebSocket for:
- Agent chat messages
- Agent flow events (task_start, task_complete)
- System log streaming

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

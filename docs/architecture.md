# Architecture

OpenSpider uses a **hierarchical multi-agent architecture** where a Manager agent orchestrates specialized Worker agents to fulfill complex requests.

## System Overview

```
┌─────────────────┐     ┌───────────────┐     ┌──────────────┐
│   WhatsApp      │────▸│               │────▸│  Manager     │
│   (Baileys)     │     │    Server     │     │  Agent 🧠    │
└─────────────────┘     │  (Express +   │     └──────┬───────┘
                        │   WebSocket)  │            │
┌─────────────────┐     │               │     ┌──────▼───────┐
│   Dashboard     │◂───▸│               │     │  Workers     │
│   (React/Vite)  │     │               │     │  ⚡ Coder    │
└─────────────────┘     └───────┬───────┘     │  🔮 Researcher│
                                │             └──────────────┘
┌─────────────────┐     ┌───────▼───────┐
│   CLI / TUI     │────▸│  Scheduler    │
│   (Commander)   │     │  (60s loop)   │
└─────────────────┘     └───────────────┘
```

## Key Files & Their Roles

| File | Purpose |
|---|---|
| `src/server.ts` | Express + WebSocket server, serves dashboard, API routes, `console.log` → WS broadcast |
| `src/whatsapp.ts` | Baileys WhatsApp connection, security firewall, message routing |
| `src/agents/ManagerAgent.ts` | Orchestrator — plans, delegates to workers, emits `agent_flow` events |
| `src/agents/WorkerAgent.ts` | Task executor — tools: search_web, browse_web, schedule_task, send_email |
| `src/agents/PersonaShell.ts` | Reads agent identity/soul/capabilities from workspace filesystem |
| `src/scheduler.ts` | 60-second heartbeat loop, executes cron jobs from `workspace/cron_jobs.json` |
| `src/llm/index.ts` | Provider factory — returns the configured LLM provider |
| `src/llm/BaseProvider.ts` | Abstract base class for all LLM providers |
| `src/cli.ts` | Commander.js CLI with all commands |
| `src/setup.ts` | Interactive onboarding wizard (Clack prompts) |
| `src/memory.ts` | Persistent memory / context management |
| `src/usage.ts` | Token usage tracking and analytics |
| `skills/send_email.py` | Gmail OAuth email sender with markdown→HTML converter |
| `dashboard/src/App.tsx` | Main dashboard (~2050 lines), all tabs/views |

## Agent Architecture

### Manager Agent (🧠 Ananta)

The Manager is the orchestrator. When it receives a user request, it:

1. **Analyzes** the request and creates a plan
2. **Delegates** tasks to Worker agents by role (Coder or Researcher)
3. **Coordinates** parallel and sequential task execution
4. **Aggregates** results into a final response

The Manager's decision format:

```json
{
  "direct_response": "...",    // If the Manager can answer directly
  "plan": [
    {
      "type": "task",
      "role": "researcher",
      "instruction": "Search for the latest AI news"
    },
    {
      "type": "parallel",
      "subtasks": [
        { "role": "coder", "instruction": "Write a Python script" },
        { "role": "researcher", "instruction": "Find documentation" }
      ]
    }
  ]
}
```

### Worker Agents

Workers are specialized executors. Each worker:

1. Receives an instruction from the Manager
2. Uses an **action loop** to reason and use tools iteratively
3. Returns a result summary to the Manager

**Available actions:**

| Action | Description |
|---|---|
| `search_web` | Search the internet via web search API |
| `browse_web` | Navigate to a URL and extract content (Playwright) |
| `read_file` | Read a file from the workspace |
| `write_file` | Write or update a file in the workspace |
| `run_command` | Execute a shell command |
| `send_email` | Send an email via Gmail OAuth |
| `schedule_task` | Create a recurring cron job |
| `wait_for_user` | Pause and wait for user input |
| `final_answer` | Return the final result to the Manager |

### PersonaShell

Each agent's persona is loaded from the filesystem at `workspace/agents/<name>/`:

- **IDENTITY.md** — Who the agent is (personality, speaking style)
- **SOUL.md** — Behavioral directives and guardrails
- **CAPABILITIES.json** — Name, role, emoji, allowed tools, token budget
- **USER.md** — Learned context about the user (evolves over time)

## Event Flow

OpenSpider uses a unique event broadcasting pattern:

```
Manager/Worker → console.log(JSON) → server.ts intercepts → WebSocket broadcast → Dashboard UI
```

1. **Agent events**: `ManagerAgent.ts` emits structured JSON via `console.log()` with types like `task_start`, `task_complete`, `agent_flow`
2. **Server intercept**: `server.ts` overrides `console.log` to detect JSON events and broadcasts them via WebSocket
3. **Dashboard render**: The React dashboard receives events and updates Agent Flow graph, Agent Chat, and System Logs in real-time

### Cron Isolation

When cron jobs execute, they use the same Manager→Worker pipeline. To prevent cron-triggered events from interfering with the dashboard:

- `scheduler.ts` maintains an `activeCronJobs` counter
- `server.ts` checks this counter and **suppresses** WebSocket broadcast of `agent_flow` events when `activeCronJobs > 0`
- This ensures the dashboard only shows user-initiated agent activity

## Server Architecture

The server (`src/server.ts`) combines:

- **Express HTTP server** on port 4001
  - Serves the built dashboard (`dashboard/dist/`)
  - REST API endpoints for agent management, config, cron jobs, usage
- **WebSocket server** on the same port
  - Real-time event streaming to dashboard
  - Agent chat message relay
- **Static file serving** for the production dashboard build

## Scheduler

The scheduler (`src/scheduler.ts`) provides autonomous task execution:

1. **Initialization**: Creates `workspace/cron_jobs.json` if missing, starts 60-second check loop
2. **Heartbeat**: Every 60 seconds, scans all jobs and executes any that are due
3. **Execution**: Creates a fresh `ManagerAgent` instance and sends the job's prompt as a system cron trigger
4. **Safety**: Updates `lastRunTimestamp` before execution to prevent rapid-fire on crash

Jobs can also be triggered manually via the dashboard or API using `runJobForcefully()`.

## Technology Stack

| Layer | Technology |
|---|---|
| **Runtime** | Node.js 22+ (TypeScript) |
| **Web Server** | Express.js |
| **Real-time** | WebSocket (ws) |
| **WhatsApp** | Baileys (@whiskeysockets/baileys) |
| **Dashboard** | React + Vite |
| **Browser Tool** | Playwright Core |
| **Email** | Python 3 + Gmail API (OAuth 2.0) |
| **Process Manager** | PM2 |
| **CLI** | Commander.js + Clack Prompts |
| **Build** | TypeScript Compiler (tsc) |

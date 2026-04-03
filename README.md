# OpenSpider 🕷️

**Autonomous Multi-Agent System for WhatsApp**

OpenSpider is an open-source, self-hosted AI agent system that connects to WhatsApp, email, and a web dashboard. It uses a hierarchical multi-agent architecture where a Manager agent orchestrates specialized Worker agents to fulfill complex tasks autonomously.

- A **Manager agent** (🧠 Ananta) receives your request, creates a plan, and delegates tasks
- **Worker agents** (⚡ Cipher the Coder, 🔮 Oracle the Researcher, 🌐 Browser Specialist) execute specific tasks using specialized tools
- Results flow back through the Manager for a polished final response

📖 **Full Documentation**: [https://vish-cloud.wl.r.appspot.com](https://vish-cloud.wl.r.appspot.com) *(or run the docs site locally)*

---

### Key Capabilities

| Capability | Description |
|---|---|
| **Multi-agent orchestration** | Manager delegates to workers with parallel task execution |
| **WhatsApp messaging** | DM and group chat support with security controls |
| **Voice messages** | Voice-in (Whisper) and voice-out (ElevenLabs) via WhatsApp |
| **Stealth Web browsing** | Playwright with human-like cursor injection `ghost-cursor` |
| **Email automation** | Gmail OAuth for sending styling HTML and reading the inbox natively |
| **Task scheduling** | Cron-style scheduled tasks managed by agents |
| **Web dashboard** | Real-time monitoring, chat, and configuration UI |
| **Theme support** | Dark, light, and system-follow theme modes |
| **Health monitoring** | Green/amber/red health indicator with component status |
| **Multiple LLMs** | Google, Anthropic, OpenAI, Ollama, and custom providers |
| **CLI management** | Full CLI for setup, daemon control, and tooling |

## Features

- 🤖 **Multi-Agent System** — Manager + Coder + Researcher + Browser Specialist agents with automatic task delegation
- **Continuous Learning Mode** — The agent can write its own code plugins to solve novel problems and permanently `save_skill` them into its global memory bank to never repeat the same work twice.
- **Bi-directional WebRTC Voice Engine** — OpenSpider hosts a millisecond-latency Twilio->OpenAI pipeline, allowing the AI to autonomously dial phone numbers (e.g. reserving restaurant tables) seamlessly via a dynamic skill!
- 📱 **WhatsApp Integration** — Full WhatsApp bot with DM/group support, mention detection, and media handling
- 🌐 **Web Dashboard** — Real-time agent chat, system telemetry, usage analytics, agent management
- ⏰ **Cron Scheduler** — Interval-based or time-of-day scheduling for autonomous tasks
- 🔌 **6 LLM Providers** — Google Gemini, Anthropic, OpenAI, Ollama (local), and custom endpoints
- 📧 **Email (Send & Read)** — Gmail OAuth integration for full inbox polling and sending formatted emails
- 🕵️ **Browser Stealth** — Headless Playwright with human-like `ghost-cursor` injection for navigating complex SPAs and bypassing bot protection
- 🛠️ **Dynamic Skills** — Create and assign custom Python and Node.js tools to agents
- 🔒 **Security** — Allowlist-based access control for WhatsApp DMs and groups

## Quick Start

### 1. Install & Link

```bash
git clone https://github.com/vbalaraman0406/OpenSpider.git
cd OpenSpider
npm install
npm link
```

### 2. Configure

```bash
openspider onboard
```

This interactive wizard generates your `.env` file with LLM provider settings.

### 3. Build & Start

```bash
npm run build
openspider gateway
```

The gateway starts on `http://localhost:4001` with the web dashboard included.

> **Note on Cloud Deployments**: If installing on a headless remote server (Ubuntu, VPS, AWS), use **Tailscale** for free, perfectly secure VPN dashboard access without exposing public ports. 
> 1. Server: `curl -fsSL https://tailscale.com/install.sh | sh` then `sudo tailscale up`
> 2. Laptop: Download the Tailscale app and log in globally.
> 3. Go to `http://<SERVER_TAILSCALE_IP>:4001` in your browser!

### 4. (Optional) GCP App Engine Deployment

If you prefer true cloud-scale hosting over local tunneling with Cloudflare/Ngrok, OpenSpider comes production-ready for **Google Cloud Platform App Engine**.

1. Ensure the `gcloud` CLI is installed and authenticated to your project.
2. Edit `app.yaml` to include any strict ENV requirements.
3. Deploy the application:
```bash
gcloud app deploy
```
4. Copy your new App Engine URL (e.g., `https://your-project.wl.r.appspot.com`) and paste it into your Twilio `.env` configuration as your `PUBLIC_URL`!

### 5. (Optional) Development Mode

```bash
npm run dev
```

Starts backend + frontend dev servers with hot-reload.

---

## Project Structure

```
OpenSpider/
├── src/                          # Backend TypeScript source
│   ├── server.ts                 # Express + WebSocket server
│   ├── whatsapp.ts               # WhatsApp connection & message routing
│   ├── scheduler.ts              # Cron job scheduler (60s heartbeat)
│   ├── memory.ts                 # Conversation memory & workspace init
│   ├── agents/
│   │   ├── ManagerAgent.ts       # Orchestrator — plans & delegates
│   │   ├── WorkerAgent.ts        # Task executor with tool loop
│   │   └── PersonaShell.ts       # Reads agent persona from filesystem
│   └── llm/                      # LLM provider implementations
├── dashboard/                    # React + Vite web dashboard
├── chrome-extension/             # Playwright cookie injection extension
├── workspace-defaults/           # Default agent configs (shipped with repo)
│   ├── agents/manager/           # Manager agent pillar files
│   ├── agents/coder/             # Coder agent pillar files
│   ├── agents/researcher/        # Researcher agent pillar files
│   ├── agents/browser-specialist/# Web navigation agent pillar files
│   └── memory.md                 # Long-term memory template
├── workspace/                    # Runtime data (auto-created on first run)
├── skills/                       # Custom Python tools
└── docs/                         # VitePress documentation site
```

## Agent Configuration

Each agent has 4 **pillar files** in `workspace/agents/<agent-id>/`:

| File | Purpose |
|---|---|
| `IDENTITY.md` | Who the agent is (name, personality, CEO/boss, company) |
| `SOUL.md` | Behavioral directives, safety rules, system architecture knowledge |
| `CAPABILITIES.json` | Allowed tools, role, emoji, operational limits |
| `USER.md` | Learned context about the user (evolves over time) |

On **first run**, defaults from `workspace-defaults/` are automatically copied to `workspace/`. Edit the files in `workspace/agents/` to customize — changes take effect **immediately** (no rebuild needed).

See [Agent Configuration](https://vish-cloud.wl.r.appspot.com/agents) for detailed docs.

## Cron Scheduling

OpenSpider supports two scheduling modes:

```json
// Interval-based: runs every N hours
{ "intervalHours": 1, "status": "enabled" }

// Time-of-day: runs once daily at a specific time
{ "preferredTime": "07:00", "status": "enabled" }
```

Manage cron jobs via the dashboard UI or the REST API at `/api/cron`.

## LLM Providers

| Provider | `DEFAULT_PROVIDER` | Local? |
|---|---|---|
| Google Gemini | `antigravity` | No |
| Anthropic Claude | `anthropic` | No |
| OpenAI | `openai` | No |
| Ollama | `ollama` | **Yes** |
| Custom | `custom` | Varies |

## Documentation

Run the docs site locally:

```bash
cd docs
npm install
npm run dev
```

## License

ISC

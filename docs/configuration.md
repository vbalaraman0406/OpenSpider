# Configuration

OpenSpider is configured through environment variables (`.env`), JSON config files in the `workspace/` directory, and per-agent capability files.

## Environment Variables

The `.env` file in the project root controls core settings. It's generated automatically by `openspider onboard`, but can be edited manually.

### Core Settings

| Variable | Description | Default |
|---|---|---|
| `DEFAULT_PROVIDER` | LLM provider to use | `antigravity` |
| `GEMINI_MODEL` | Model name for Google/Antigravity provider | `gemini-2.5-pro` |
| `FALLBACK_MODEL` | Fallback model if primary fails | _(empty)_ |
| `ENABLE_WHATSAPP` | Enable WhatsApp channel | `true` |

### Provider-Specific Keys

Depending on your chosen provider, set the relevant API key:

| Variable | Provider |
|---|---|
| `GEMINI_API_KEY` | Google Gemini |
| `ANTHROPIC_API_KEY` | Anthropic Claude |
| `OPENAI_API_KEY` | OpenAI |
| `OLLAMA_MODEL` | Ollama (local, no API key needed) |
| `CUSTOM_API_KEY` | Custom OpenAI-compatible endpoint |
| `CUSTOM_BASE_URL` | Custom provider base URL |
| `CUSTOM_MODEL` | Custom provider model name |

### Example `.env` Files

::: code-group

```env [Google Gemini]
DEFAULT_PROVIDER=antigravity
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.5-pro
ENABLE_WHATSAPP=true
```

```env [Anthropic Claude]
DEFAULT_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-opus-4
ENABLE_WHATSAPP=true
```

```env [OpenAI]
DEFAULT_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
ENABLE_WHATSAPP=true
```

```env [Ollama (Local)]
DEFAULT_PROVIDER=ollama
OLLAMA_MODEL=llama3
ENABLE_WHATSAPP=true
```

```env [Custom Endpoint]
DEFAULT_PROVIDER=custom
CUSTOM_API_KEY=your-key
CUSTOM_BASE_URL=https://your-api.example.com/v1
CUSTOM_MODEL=your-model-name
ENABLE_WHATSAPP=true
```

:::

## LLM Providers

OpenSpider supports 6 built-in LLM providers. Switch between them by changing `DEFAULT_PROVIDER` in your `.env`.

| Provider | `DEFAULT_PROVIDER` Value | Local? | Notes |
|---|---|---|---|
| Google Gemini | `antigravity` | No | Default. Supports Gemini 2.5 Pro, Flash, etc. |
| Antigravity Internal | `antigravity-internal` | No | Internal proxy for advanced models |
| Anthropic | `anthropic` | No | Claude Opus, Sonnet, Haiku |
| OpenAI | `openai` | No | GPT-4o, GPT-4, etc. |
| Ollama | `ollama` | **Yes** | Run models locally (Llama 3, Mistral, etc.) |
| Custom | `custom` | Varies | Any OpenAI-compatible API endpoint |

To view your current configuration:

```bash
openspider models list
```

### Automatic Backup Fallback Chain

If your primary LLM encounters a rate limit (429), authentication error (401), server error (500), or API timeout, OpenSpider automatically cascades through a built-in fallback chain so the task does not crash.

| Priority | Backup Level | Required Env Vars | Description |
|---|---|---|---|
| **1** | **Primary Provider** | e.g. `GEMINI_API_KEY` | The default provider as configured above |
| **2** | **Legacy Fallback** | `FALLBACK_MODEL` | Simple text model override (e.g. `gemini-2.5-flash`) |
| **3** | **Internal Fallback** | `(Antigravity only)` | Safe internal step down to `gemini-3.1-pro` → `gemini-2.5-pro` → `flash` to preserve quota before external failover |
| **4** | **DeepSeek Backup** | `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL` | DeepSeek explicitly acts as the strongest, cheapest first external backup |
| **5** | **NVIDIA Backup 1** | `NVIDIA_API_KEY_1`, `NVIDIA_MODEL_1` | First NVIDIA API endpoint (e.g. Nemotron) |
| **6** | **NVIDIA Backup 2** | `NVIDIA_API_KEY_2`, `NVIDIA_MODEL_2` | Second NVIDIA API endpoint |

You can safely add these backup models at any time by running:
```bash
openspider models add
```

## Config Files

### WhatsApp Configuration

**File:** `workspace/whatsapp_config.json`

Controls who can message the agent and how it responds in groups.

```json
{
  "dmPolicy": "allowlist",
  "allowedDMs": ["14155551234"],
  "groupPolicy": "allowlist",
  "allowedGroups": [
    {
      "jid": "120363423460684848@g.us",
      "mode": "mention"
    }
  ],
  "botMode": "mention"
}
```

| Field | Type | Description |
|---|---|---|
| `dmPolicy` | `"allowlist"` \| `"open"` | DM access control |
| `allowedDMs` | `string[]` | Phone numbers permitted to DM (without `+`) |
| `groupPolicy` | `"allowlist"` \| `"open"` | Group access control |
| `allowedGroups` | `object[]` | Groups the bot participates in |
| `allowedGroups[].jid` | `string` | WhatsApp group JID |
| `allowedGroups[].mode` | `"mention"` \| `"listen"` | Per-group response mode |
| `botMode` | `"mention"` \| `"listen"` | Global fallback mode for groups |

See [Channels](/channels) for detailed configuration.

### Cron Jobs

**File:** `workspace/cron_jobs.json`

Stores scheduled tasks. Jobs can use **interval-based** scheduling (every N hours) or **time-of-day** scheduling (run once daily at a specific time).

::: code-group

```json [Interval-Based (every N hours)]
[
  {
    "id": "cron-abc123",
    "description": "Iran War & Market Update",
    "prompt": "Search for latest Iran conflict news and market reactions...",
    "intervalHours": 1,
    "lastRunTimestamp": 1709337600000,
    "agentId": "manager",
    "status": "enabled"
  }
]
```

```json [Time-of-Day (daily at specific time)]
[
  {
    "id": "cron-xyz789",
    "description": "Daily Weather Report",
    "prompt": "Fetch the 5-day forecast for Vancouver, WA and send via email...",
    "intervalHours": 24,
    "lastRunTimestamp": 0,
    "agentId": "manager",
    "status": "enabled",
    "preferredTime": "07:00"
  }
]
```

:::

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Unique job identifier |
| `description` | `string` | Human-readable description |
| `prompt` | `string` | The instruction sent to the Manager agent |
| `intervalHours` | `number` | Hours between executions (ignored when `preferredTime` is set) |
| `lastRunTimestamp` | `number` | Unix ms timestamp of last execution (set to `0` for time-of-day jobs to trigger on next occurrence) |
| `agentId` | `string` | Which agent runs the job |
| `status` | `"enabled"` \| `"disabled"` | Toggle job on/off |
| `preferredTime` | `string` _(optional)_ | Time of day to run (e.g. `"07:00"`, `"14:30"`). When set, the job runs **once daily** at this time in the server's local timezone |

::: tip Time-of-Day Scheduling
When `preferredTime` is set, the scheduler checks every 60 seconds if the current time is within a 5-minute window of the preferred time **and** the job hasn't already run today. This is ideal for daily reports like weather forecasts or news digests.
:::

### Agent Capabilities

**File:** `workspace/agents/<agent-name>/CAPABILITIES.json`

Defines each agent's name, role, tools, and budget.

```json
{
  "name": "Ananta",
  "role": "Manager",
  "emoji": "🧠",
  "allowedTools": ["delegate_task", "read_file", "search_web", "ask_user"],
  "maxDelegationDepth": 3,
  "budgetTokens": 100000
}
```

### Agent Persona Files

Each agent's directory under `workspace/agents/` contains:

| File | Purpose |
|---|---|
| `CAPABILITIES.json` | Name, role, emoji, tools, token budget |
| `IDENTITY.md` | Agent persona description / personality |
| `SOUL.md` | Behavioral directives and guardrails |
| `USER.md` | Learned context about the user (evolves over time) |

## Build & Deploy

### Build Commands

```bash
# Build everything (backend + frontend)
npm run build

# Build backend only (TypeScript → dist/)
npm run build:backend

# Build frontend only (Vite → dashboard/dist/)
npm run build:frontend
```

### Development Mode

```bash
# Run backend + frontend dev servers concurrently
npm run dev

# Backend only (with hot-reload via nodemon)
npm run dev:backend

# Frontend only (Vite dev server)
npm run dev:frontend
```

### Production Deployment

```bash
# Build everything
npm run build

# Start with PM2
openspider start

# Or restart if already running
pm2 restart all
```

## Workspace Defaults & First Run

OpenSpider ships with a `workspace-defaults/` directory containing all default agent configurations. On **first run**, these are automatically copied to `workspace/`.

### What's Included

| Default File | Purpose |
|---|---|
| `agents/manager/IDENTITY.md` | Manager agent persona (customize with your name/company) |
| `agents/manager/SOUL.md` | Safety directives + system architecture knowledge |
| `agents/manager/CAPABILITIES.json` | Manager tools, role, emoji |
| `agents/manager/USER.md` | Empty user context template |
| `agents/coder/*` | Coder agent pillar files |
| `agents/researcher/*` | Researcher agent pillar files |
| `memory.md` | Long-term memory template |

### Customization After Install

After first run, edit the files in `workspace/agents/` to personalize:

```bash
# Set your name as the manager's boss
nano workspace/agents/manager/IDENTITY.md

# Modify behavioral rules
nano workspace/agents/manager/SOUL.md
```

Pillar files are read at **runtime** — changes take effect immediately without rebuilding.

See [Agent Configuration](/agents) for detailed customization options.

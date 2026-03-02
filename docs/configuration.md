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

Stores scheduled tasks created by agents via the `schedule_task` tool.

```json
[
  {
    "id": "abc123",
    "description": "Daily news summary",
    "prompt": "Search for the latest tech news and send a summary email",
    "intervalHours": 24,
    "lastRunTimestamp": 1709337600000,
    "agentId": "manager",
    "status": "enabled"
  }
]
```

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Unique job identifier |
| `description` | `string` | Human-readable description |
| `prompt` | `string` | The instruction sent to the Manager agent |
| `intervalHours` | `number` | Hours between executions |
| `lastRunTimestamp` | `number` | Unix ms timestamp of last execution |
| `agentId` | `string` | Which agent created the job |
| `status` | `"enabled"` \| `"disabled"` | Toggle job on/off |

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

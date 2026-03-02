# Getting Started

This guide will walk you through installing, configuring, and running OpenSpider on your machine.

## Prerequisites

| Requirement | Version | Purpose |
|---|---|---|
| **Node.js** | ≥ 22 | Runtime for the backend and CLI |
| **npm** | ≥ 10 | Package management |
| **Python 3** | ≥ 3.8 | Required for the email skill (`send_email.py`) |
| **Git** | Latest | Cloning the repository |

Check your versions:

```bash
node --version    # Should be v22.x or higher
npm --version     # Should be v10.x or higher
python3 --version # Should be 3.8+
git --version
```

::: tip
If you don't have Node.js 22+, the install script will attempt to install it via [NVM](https://github.com/nvm-sh/nvm) automatically.
:::

## Installation

### Option A: One-Line Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/vbalaraman/OpenSpider/main/install.sh | bash
```

This script will:
1. Check for Node.js ≥22 (installs via NVM if missing)
2. Clone the repository to `~/.openspider`
3. Install all dependencies (`npm install`)
4. Build the backend and frontend (`npm run build`)
5. Link the `openspider` CLI globally (`npm link`)

### Option B: Manual Install

```bash
# Clone the repository
git clone https://github.com/vbalaraman/OpenSpider.git
cd OpenSpider

# Install dependencies
npm install

# Build backend (TypeScript → dist/) and frontend (Vite → dashboard/dist/)
npm run build

# Link the CLI globally
npm link
```

After installation, verify the CLI is available:

```bash
openspider --version
# Output: 1.0.0
```

## Initial Setup

Run the onboarding wizard to configure your LLM provider and agent persona:

```bash
openspider onboard
```

The wizard will guide you through:

1. **LLM Provider Selection** — Choose from Google Gemini, Anthropic Claude, OpenAI, Ollama (local), or a custom endpoint
2. **API Key Configuration** — Enter your API key for the selected provider
3. **Model Selection** — Pick the specific model to use (e.g., `gemini-2.5-pro`, `claude-opus-4`, `gpt-4o`)
4. **Agent Persona** — Configure your Manager agent's name and personality
5. **WhatsApp Setup** — Optionally connect WhatsApp by scanning a QR code

The wizard generates a `.env` file with your configuration:

```env
DEFAULT_PROVIDER=antigravity
GEMINI_MODEL=gemini-2.5-pro
FALLBACK_MODEL=
ENABLE_WHATSAPP=true
```

## Starting the Gateway

### Foreground Mode (Development)

```bash
openspider gateway
```

Runs the gateway in the foreground with live logs. Press `Ctrl+C` to stop. Best for development and debugging.

### Background Mode (Production)

```bash
openspider start
```

Starts the gateway as a background daemon using PM2. The server runs on `http://localhost:4001`.

```bash
# View real-time logs
openspider logs

# Stop the daemon
openspider stop
```

## Accessing the Dashboard

```bash
openspider dashboard
```

Opens the web dashboard at [http://localhost:4001](http://localhost:4001) in your default browser. The dashboard provides:

- **Agent Chat** — Talk to your agents directly
- **Agent Flow** — Visualize task delegation in real-time
- **System Logs** — Filterable, searchable, exportable logs
- **Workspace** — Browse agent files and configuration
- **WhatsApp Security** — Manage DM/group allowlists

## Terminal UI

For a terminal-based chat experience:

```bash
openspider tui
```

## Connecting WhatsApp

If you didn't connect WhatsApp during onboarding:

```bash
openspider channels login
```

This watches for QR codes from the running gateway. Scan the QR code with your phone's WhatsApp to link OpenSpider.

## What You Now Have

After completing setup, you have:

- ✅ A running OpenSpider gateway (HTTP + WebSocket server)
- ✅ Configured LLM provider with your chosen model
- ✅ Agent personas ready (Manager, Coder, Researcher)
- ✅ Web dashboard accessible at `http://localhost:4001`
- ✅ WhatsApp connected (if configured)

## Next Steps

- **[Configuration](/configuration)** — Fine-tune providers, models, and environment variables
- **[Channels](/channels)** — Set up WhatsApp DM/group policies and security
- **[Dashboard](/dashboard)** — Explore the full dashboard feature set
- **[Tools & Skills](/tools-and-skills)** — Enable email, browsing, and scheduling capabilities
- **[CLI Reference](/cli-reference)** — Complete command reference

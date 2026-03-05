# Getting Started

This guide walks you through installing and running OpenSpider for the first time — from zero to a fully working AI agent gateway.

## Prerequisites

| Requirement | Version | Purpose |
|---|---|---|
| **Node.js** | ≥ 22 | Runtime for the backend and CLI |
| **npm** | ≥ 10 | Package management |
| **Python 3** | ≥ 3.8 | Required for the email skill (`send_email.py`) |
| **Git** | Latest | Cloning the repository |

### Detailed Prerequisite Setup

If you do not have these installed already, follow these steps based on your operating system:

#### macOS / Linux
We recommend using **Homebrew** (macOS) or your distro's package manager. For Node.js, we strongly recommend `nvm`.

1. **Install Git & Python:**
   - macOS: `brew install git python` (Requires [Homebrew](https://brew.sh/))
   - Ubuntu/Debian: `sudo apt update && sudo apt install git python3 python3-pip`
2. **Install Node.js 22 via NVM:**
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
   # Restart your terminal, then:
   nvm install 22
   nvm use 22
   ```

#### Windows
We strongly recommend running OpenSpider inside **WSL2 (Windows Subsystem for Linux)**.
1. Open PowerShell as Administrator and run: `wsl --install`
2. Restart your computer and open the new "Ubuntu" terminal.
3. Follow the Linux instructions above inside that terminal.

---

Verify your environment is ready:

```bash
node --version    # Should output v22.x.x
npm --version     # Should output v10.x.x
python3 --version # Should output Python 3.8+
git --version
```

::: tip Automated Node.js Install
The one-line `curl` installer below will attempt to automatically install `nvm` and Node.js 22 if it detects they are missing.
:::

---

## Step 1: Install

### Option A — One-Line Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/vbalaraman0406/OpenSpider/main/install.sh | bash
```

This script:
1. Checks for Node.js ≥ 22 (installs via NVM if missing)
2. Clones the repo to `~/.openspider`
3. Runs `npm install` for all dependencies
4. Builds the backend and frontend
5. Links the `openspider` CLI globally

### Option B — Manual Install

```bash
git clone https://github.com/vbalaraman0406/OpenSpider.git
cd OpenSpider
npm install
npm run build
npm link
```

Verify the CLI is available:

```bash
openspider --version
```

---

## Step 2: Run the Onboarding Wizard

```bash
openspider onboard
```

The wizard walks you through:

1. **LLM Provider** — Choose from Google Gemini, Anthropic Claude, OpenAI, Ollama (local), or any OpenAI-compatible endpoint
2. **API Key** — Enter your provider's API key
3. **Model** — Pick the specific model (e.g. `gemini-2.5-pro`, `claude-opus-4`, `gpt-4o`)
4. **Agent Persona** — Set the Manager agent's name and personality
5. **WhatsApp** — Optionally connect WhatsApp by scanning a QR code

The wizard creates a `.env` file in the project root:

```env
DEFAULT_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-pro
ENABLE_WHATSAPP=true

# Auto-generated security keys (do not share)
DASHBOARD_API_KEY=<generated>
OPENSPIDER_HOOK_TOKEN=<generated>
```

::: warning Generated Security Keys
`DASHBOARD_API_KEY` and `OPENSPIDER_HOOK_TOKEN` are auto-generated during onboarding. They protect your dashboard and webhook from unauthorized access. **Never commit `.env` to version control.**
:::

---

## Step 3: Start the Gateway

### Background Mode (Recommended for daily use)

```bash
openspider start
```

Starts the gateway as a background daemon via PM2 on `http://localhost:4001`.

```bash
openspider logs    # Stream live logs
openspider stop    # Stop the daemon
```

### Foreground Mode (Development / Debugging)

```bash
openspider gateway
```

Runs the gateway in the foreground with live console output. Press `Ctrl+C` to stop.

---

## Step 4: Open the Dashboard

```bash
openspider dashboard
```

Opens `http://localhost:4001` in your browser. The dashboard includes:

| Tab | What it does |
|---|---|
| **Agent Chat** | Talk directly to your agents, attach files or images |
| **Agent Flow** | Watch task delegation visualized in real-time |
| **System Logs** | Filterable, searchable, exportable logs |
| **Workspace** | Browse agent files, personas, and cron jobs |
| **Channels** | Manage WhatsApp DM/group allowlists |
| **Usage** | Token and cost analytics per model |
| **Settings** | Configure voice, cron jobs, and agent skills |

The dashboard authenticates automatically using the `DASHBOARD_API_KEY` from your `.env`. No login screen — it just works locally.

---

## Step 5: Connect WhatsApp (Optional)

If you skipped WhatsApp during onboarding:

```bash
openspider channels login
```

Scan the QR code with WhatsApp on your phone (`Linked Devices → Link a Device`). Once linked, OpenSpider will respond to your WhatsApp messages automatically.

::: tip DM Allowlist
After linking, add your phone number to the DM allowlist via the dashboard under **Channels → WhatsApp Security** — or only a strict allowlist of numbers can message your agent.
:::

---

## Step 6: Set Up Voice Messages (Optional)

To enable voice note support (voice-in via Whisper, voice-out via ElevenLabs):

1. Install Whisper: `pip3 install openai-whisper`
2. Get an [ElevenLabs API key](https://elevenlabs.io) and add to `.env`:
   ```env
   ELEVENLABS_API_KEY=your_key_here
   ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
   ```
3. Restart the gateway: `pm2 restart openspider-gateway`

Voice settings (voice model, default voice) can be changed anytime in the dashboard under **Settings → Voice**.

---

## Step 7: Set Up Email Sending (Optional)

To let agents send emails on your behalf via Gmail OAuth:

```bash
openspider tools email setup
```

Follow the OAuth flow to authorize your Gmail account. Credentials are stored in `workspace/gmail_credentials.json` and `workspace/gmail_token.json` (both in `.gitignore`).

---

## ✅ You're Ready

After completing setup you have:

- ✅ OpenSpider gateway running on `http://localhost:4001`
- ✅ Dashboard secured with a generated API key
- ✅ LLM provider configured with your chosen model
- ✅ Manager + Worker agents ready (Coder, Researcher)
- ✅ WhatsApp connected (if configured)
- ✅ Voice notes working (if configured)

---

## Next Steps

- **[Configuration](/configuration)** — Fine-tune providers, models, and environment variables
- **[Security](/security)** — API authentication, CORS, webhook tokens, and command sandbox
- **[Dashboard](/dashboard)** — Explore the full dashboard feature set
- **[Channels](/channels)** — WhatsApp DM/group policies and security allowlists
- **[Tools & Skills](/tools-and-skills)** — Email, browsing, scheduling, and custom skills
- **[CLI Reference](/cli-reference)** — Complete command reference

## Troubleshooting

See the **[Troubleshooting Guide](/troubleshooting)** for common issues like QR code not showing, WhatsApp disconnects, LLM errors, and dashboard connection problems.

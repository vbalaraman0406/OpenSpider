# Tools & Skills

OpenSpider agents come equipped with built-in tools for web interaction, file operations, email, and task scheduling. The system also supports dynamic skill metadata for extending capabilities.

## Built-in Agent Tools

### Web Search

Agents can search the internet for real-time information.

```json
{
  "action": "search_web",
  "args": "latest AI news March 2026"
}
```

Used by the Researcher agent (🔮 Oracle) for gathering information.

---

### Web Browsing

Agents can navigate to any URL and extract page content using a headless Playwright browser.

```json
{
  "action": "browse_web",
  "command": "navigate",
  "url": "https://example.com/article"
}
```

**Features:**
- Full page content extraction
- Headless Chromium via Playwright Core
- Configurable via `workspace/browser.json`
- **Native Chatbot Interaction:** The `type_and_enter` command mimics human typing speed natively (bypassing bot detection) and enforces an automatic 4-second delay after submission to accommodate for modern React chatbot response times.

#### Bypassing Bot Detection (Cookie Injection)

For websites with strict bot protection (like Cloudflare) or sites requiring manual login, OpenSpider includes a Chrome Extension that can sync your personal browser session into the agent's headless browser.

1. Install the OpenSpider Browser Relay extension in Google Chrome.
2. Get your securely generated API token by running `openspider token`.
3. Paste the token into the Extension popup's **Gateway Token** field.
4. Log into the protected website normally as a human in Chrome.
5. Click **"Export Cookies to OpenSpider"** in the extension popup.

The agent will now bypass login screens and Cloudflare blocks because it is authenticated using your exact session!

---

### File Operations

#### Read File

Read any file from the workspace directory:

```json
{
  "action": "read_file",
  "args": "agents/manager/IDENTITY.md"
}
```

#### Write File

Create or update files in the workspace:

```json
{
  "action": "write_file",
  "target": "reports/summary.md",
  "args": "# Report\n\nContent here..."
}
```

---

### Run Command

Execute shell commands on the host system:

```json
{
  "action": "run_command",
  "args": "ls -la workspace/"
}
```

::: warning
Shell command execution gives agents significant system access. Monitor agent activity via the dashboard logs.
:::

---

### Send Email

Send emails via Gmail OAuth with automatic markdown-to-HTML conversion.

```json
{
  "action": "send_email",
  "to": "recipient@example.com",
  "subject": "Daily Report",
  "body": "# Summary\n\n**Key findings:**\n- Item 1\n- Item 2"
}
```

#### How It Works

1. The WorkerAgent invokes `python3 skills/send_email.py` with `--to`, `--subject`, and `--body` arguments
2. `send_email.py` converts the markdown body to HTML using a zero-dependency converter
3. The HTML is wrapped in a professional email template with:
   - Gradient header with `♾️ {Agent Name}` (read from `IDENTITY.md`)
   - Dark-themed body (`#111127` background)
   - Footer: "Powered by ♾️ {Agent Name} — OpenSpider Agent System"
4. Sent via Gmail API using stored OAuth tokens

#### Email Setup

Before agents can send email, configure OAuth credentials:

```bash
# Step 1: Set up OAuth credentials
openspider tools email setup

# Step 2: Verify it works
openspider tools email test --to your@email.com
```

**Prerequisites — Google Cloud Setup:**

OpenSpider agents require an OAuth token with both `gmail.send` and `gmail.readonly` scopes to act autonomously on your behalf. Since this token grants access to your personal inbox, you must generate it securely via your own Google Cloud project.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown in the top left and create a **New Project** (e.g. "OpenSpider Mail").
3. Go to **APIs & Services > Library**.
4. Search for "**Gmail API**" and click **Enable**.
5. Go to **APIs & Services > OAuth consent screen**.
   - Choose **External** user type and click Create.
   - Fill in App Name ("OpenSpider"), user support email, and developer contact information.
   - Click **Save and Continue** until you reach the **Test Users** screen.
   - Click **Add Users** and add your own personal Gmail address. Click Save.
6. Go to **APIs & Services > Credentials**.
7. Click **+ Create Credentials > OAuth client ID**.
8. Select **Desktop app** as the Application type. Name it "OpenSpider Desktop" and click Create.
9. An overlay will appear. Click **Download JSON** to save the `client_secret_xyz.json` file to your computer.

#### Running the Setup Wizard

Once you have downloaded the JSON file, configure OpenSpider:

1. Run the setup wizard in your terminal:
   ```bash
   openspider tools email setup
   ```
2. Paste the **absolute path** to the downloaded JSON file (e.g. `/Users/YourName/Downloads/client_secret_xyz.json`).
3. The wizard will copy this file to `workspace/gmail_credentials.json`.
4. A browser window will automatically open asking you to log into Google and grant permissions.
5. Click **Continue**, select the test user email you added earlier, and check both the "Send" and "Read" boxes.
6. Once you see "Authentication flows completed," OpenSpider saves the access token to `workspace/gmail_token.json`.

Your agents can now autonomously read and send emails without needing to re-authenticate!

---

### Schedule Task

Agents can create recurring cron jobs that execute automatically:

```json
{
  "action": "schedule_task",
  "args": "Send a daily tech news summary email to user@example.com every morning"
}
```

#### How It Works

1. The agent parses the request and creates a cron job entry
2. The job is saved to `workspace/cron_jobs.json` with:
   - Description, prompt, interval (in hours), status
   - `lastRunTimestamp` set to `Date.now()` (waits a full interval before first run)
3. The scheduler's 60-second heartbeat loop picks up the job
4. On each trigger, a fresh `ManagerAgent` instance processes the job's prompt
5. Agent flow events from cron jobs are isolated from the dashboard UI

#### Cron Job Format

```json
{
  "id": "unique-id",
  "description": "Daily tech news email",
  "prompt": "Search for today's top tech news and send a summary email to user@example.com",
  "intervalHours": 24,
  "lastRunTimestamp": 1709337600000,
  "agentId": "manager",
  "status": "enabled"
}
```

#### Managing Cron Jobs

- **Dashboard** → Cron Jobs tab: view, enable/disable, manually trigger
- **API**: `POST /api/cron/:id/run` to force-trigger a job
- **File**: Edit `workspace/cron_jobs.json` directly

---

### Wait for User

Pause agent execution and wait for user input:

```json
{
  "action": "wait_for_user",
  "message": "Should I proceed with sending the email?"
}
```

---

## Dynamic Skills & Continuous Learning

OpenSpider agents operate in a **Continuous Learning Mode**. They are not restricted to hard-coded TypeScript tools! 

If you ask an agent to perform a novel task (like formatting a specialized PDF or interacting with an API), the agent will:
1. Natively write a Python or Node.js script using `write_script`.
2. Test the script using `execute_script`.
3. Call **`save_skill`** to permanently commit the script to its global memory bank!

### Skill Catalog Structure

When an agent calls `save_skill`, OpenSpider creates a `.json` metadata file in the `skills/` directory alongside the generated script. For example:

**`skills/voice_call.json`**
```json
{
    "name": "voice_call",
    "description": "Call a business or person natively using Twilio WebRTC",
    "instructions": "Execute script passing phoneNumber and task...",
    "language": "js"
}
```

Whenever OpenSpider boots up or starts a new session, it pulls this catalog into its prompt. The agent NEVER has to rewrite the same script twice. You can view all saved skills in the Dashboard's Skills tab.

### Available Pre-loaded Skills

| Skill | Description |
|---|---|
| `voice_call` | Autonomous Phone Dialing via Twilio WebRTC |
| `send_email` | Gmail-based email sending via OAuth |

## Gmail Webhooks

For event-driven automation, OpenSpider can receive Gmail push notifications:

```bash
# Set up GCP Pub/Sub for Gmail webhooks
openspider webhooks gmail setup -p YOUR_PROJECT_ID -a your@gmail.com

# Start the webhook listener
openspider webhooks gmail run
```

This enables agents to react to incoming emails automatically.

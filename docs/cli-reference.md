# CLI Reference

OpenSpider provides a full CLI for setup, daemon management, channel control, and tooling. All commands are available after running `npm link` in the project root.

```bash
openspider [command] [options]
```

## Core Commands

### `openspider onboard`

Run the interactive setup wizard to configure your LLM provider, API keys, model, agent persona, and optionally WhatsApp.

```bash
openspider onboard
```

The wizard generates a `.env` file and sets up the `workspace/` directory structure.

---

### `openspider gateway`

Start the core agent engine and HTTP/WebSocket server in the **foreground**.

```bash
openspider gateway
```

The server starts on `http://localhost:4001`. Press `Ctrl+C` to stop. Best for development.

---

### `openspider start`

Start the gateway as a **background daemon** using PM2.

```bash
openspider start
```

After starting, the daemon runs independently. Use `openspider logs` to monitor and `openspider stop` to shut down.

---

### `openspider stop`

Stop the background daemon.

```bash
openspider stop
```

---

### `openspider logs`

Stream real-time logs from the background daemon (last 100 lines + live tail).

```bash
openspider logs
```

Press `Ctrl+C` to stop streaming.

---

### `openspider dashboard`

Open the web dashboard in your default browser.

```bash
openspider dashboard
```

Opens `http://localhost:4001` automatically.

---

### `openspider token`

Print the secure Gateway Token required to authenticate the OpenSpider Browser Relay Chrome Extension.

```bash
openspider token
```

---

### `openspider status`

Show the current gateway status, version, provider, and PM2 uptime.

```bash
openspider status
```

**Example output:**

```
🕷️  OpenSpider Status
──────────────────────────────────────────────────
Version:          v2.0.2
Provider:         anthropic
API Port:         4001
Dashboard:        http://localhost:4001
──────────────────────────────────────────────────
Gateway:          ✅ online  (uptime: 142 min, restarts: 0)
```

---

### `openspider tui`

Launch the Terminal User Interface for chatting with the agent directly in your terminal.

```bash
openspider tui
```

---

## Channel Commands

### `openspider channels login`

Watch for QR codes from the running gateway and display them in the terminal for WhatsApp authentication.

```bash
openspider channels login
```

The command polls for new QR codes every second. Once connected, it exits automatically.

---

### `openspider channels whatsapp login`

Initialize a fresh WhatsApp connection directly (standalone, not via the gateway).

```bash
openspider channels whatsapp login
```

---

## Tool Commands

### `openspider tools email setup`

Configure Gmail OAuth 2.0 credentials for the email skill.

```bash
openspider tools email setup
```

**Steps:**
1. Download OAuth Client ID JSON from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Run the command and provide the path to your credentials JSON
3. A browser window opens for Google OAuth authentication
4. Token is saved to `workspace/gmail_token.json`

---

### `openspider tools email test`

Send a test email to verify the email configuration.

```bash
openspider tools email test [options]
```

| Option | Description | Default |
|---|---|---|
| `-t, --to <email>` | Recipient email address | _(prompted)_ |
| `-s, --subject <text>` | Email subject line | `Test from OpenSpider` |
| `-b, --body <text>` | Email body content | `This is a test email...` |

**Example:**

```bash
openspider tools email test --to user@example.com --subject "Hello" --body "Test message"
```

---

## Webhook Commands

### `openspider webhooks gmail setup`

Automate GCP Pub/Sub setup for Gmail push webhook notifications.

```bash
openspider webhooks gmail setup [options]
```

| Option | Description |
|---|---|
| `-p, --project <id>` | Google Cloud Project ID |
| `-a, --account <email>` | Gmail account to monitor |

This command:
1. Sets the active GCP project
2. Enables Gmail and Pub/Sub APIs
3. Creates the `gog-gmail-watch` Pub/Sub topic
4. Grants Gmail API the Publisher role
5. Outputs next steps for starting the watch and webhook listener

---

### `openspider webhooks gmail run`

Start the gateway with webhook listener enabled.

```bash
openspider webhooks gmail run
```

---

## Model Commands

### `openspider models list`

Display the currently configured LLM provider and all available models.

```bash
openspider models list
```

**Example output:**

```
🕷️  OpenSpider Model Configuration:
──────────────────────────────────────────────────
Default Provider:   anthropic
Primary Model:      claude-opus-4-5
Fallback Model:     None
──────────────────────────────────────────────────

All configured providers:
  ✅ anthropic    (model: claude-opus-4-5)
  ✅ openai       (model: gpt-4o)

Config file: /Users/name/OpenSpider/.env
```

The config file path is shown so you can quickly find and edit your settings.

---

## Global Options

| Option | Description |
|---|---|
| `-V, --version` | Display version number |
| `-h, --help` | Display help for command |

```bash
openspider --version
openspider --help
openspider <command> --help
```

---

## Command Summary

| Command | Description |
|---|---|
| `onboard` | Interactive setup wizard |
| `gateway` | Start server (foreground) |
| `start` | Start daemon (background) |
| `stop` | Stop daemon |
| `status` | Show gateway status and uptime |
| `logs` | Stream daemon logs |
| `dashboard` | Open web dashboard |
| `tui` | Terminal chat UI |
| `channels login` | WhatsApp QR auth (from gateway) |
| `channels whatsapp login` | Direct WhatsApp connection |
| `tools email setup` | Gmail OAuth setup |
| `tools email test` | Send test email |
| `webhooks gmail setup` | GCP Pub/Sub setup |
| `webhooks gmail run` | Start webhook listener |
| `models list` | Show configured models |

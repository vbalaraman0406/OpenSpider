# Security

OpenSpider provides multiple layers of security to control who can interact with your agents and how they behave.

## Dashboard API Authentication

As of v2.0.1, **all API endpoints and WebSocket connections require an API key**. This prevents anyone on your local network from accessing or controlling your agents without authorization.

### How It Works

Your API key is auto-generated during setup and stored in `.env`:

```env
DASHBOARD_API_KEY=<64-character hex key>
```

The dashboard frontend automatically reads this key from `dashboard/.env` (via `VITE_API_KEY`) and attaches it to every API request and WebSocket connection.

### Authenticating API Calls

If you are calling the API directly (e.g., from a script or external tool), provide the key as a header:

```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:4001/api/agents
```

Or via the `Authorization` header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:4001/api/agents
```

### WebSocket Authentication

The WebSocket server validates the key via query parameter on connect:

```
ws://localhost:4001/?apiKey=YOUR_API_KEY
```

### Public Endpoints

The following endpoint is intentionally unauthenticated so health monitoring tools work without credentials:

| Endpoint | Reason |
|---|---|
| `GET /api/health` | External uptime monitors |
| `POST /hooks/gmail` | Google Pub/Sub webhook (uses its own `OPENSPIDER_HOOK_TOKEN`) |

### Rotating Your API Key

To rotate the dashboard API key:

1. Generate a new key: `node -e "const c=require('crypto'); console.log(c.randomBytes(32).toString('hex'));"`
2. Update `DASHBOARD_API_KEY` in `.env`
3. Update `VITE_API_KEY` in `dashboard/.env` to match
4. Rebuild the frontend: `npm run build:frontend`
5. Restart the server: `pm2 restart openspider-gateway`

---

## CORS Policy

The server enforces **localhost-only CORS**. Requests from external origins (other domains) are rejected. This prevents cross-site attacks from websites open in the same browser.

Allowed origins: `http://localhost:*` and `http://127.0.0.1:*` only.

---

## Gmail Webhook Authentication

The Gmail webhook (`POST /hooks/gmail`) is protected by a separate long-lived token:

```env
OPENSPIDER_HOOK_TOKEN=<48-character hex token>
```

Pass this token when registering your Google Pub/Sub subscription URL:

```
https://your-server/hooks/gmail?token=YOUR_TOKEN
```

::: warning
If `OPENSPIDER_HOOK_TOKEN` is not set or is fewer than 16 characters, the webhook will reject **all** incoming calls with `403`. This fail-safe prevents the old default string `OPENSPIDER_HOOK_TOKEN` from being a valid credential.
:::

---

## WhatsApp Access Control

### DM Allowlist

By default, OpenSpider only accepts direct messages from numbers in the allowlist:

```json
{
  "dmPolicy": "allowlist",
  "allowedDMs": ["14155551234"]
}
```

- Phone numbers are stored **without** the `+` prefix
- Only listed numbers can send DMs to the agent
- Setting `dmPolicy` to `"open"` disables this control (not recommended for production)

### Group Allowlist

Only specified WhatsApp groups are monitored:

```json
{
  "groupPolicy": "allowlist",
  "allowedGroups": [
    {
      "jid": "120363423460684848@g.us",
      "mode": "mention"
    }
  ]
}
```

Groups not in the allowlist are completely ignored.

## Per-Group Response Modes

Each group can be independently configured:

| Mode | Behavior | Use Case |
|---|---|---|
| **Mention** | Only responds when `@mentioned` | Busy groups where you want targeted interaction |
| **Listen** | Responds to every message | Small/dedicated groups where every message is relevant |

---

## Command Sandbox

When the AI agent runs shell commands via the `run_command` tool, `DynamicExecutor` enforces:

1. **Metacharacter blocking** — Commands with `;`, `|`, `&`, `` ` ``, `$()`, `<`, `>` are rejected before execution.
2. **Regex blocklist** — Catches bypass variants of dangerous patterns:
   - `rm -rf`, `rm -f`, `rmdir`, `mkfs`, `dd if=`
   - `sudo`, `chown`, `chmod` (all variants)
   - `curl ... | bash`, `wget ... | bash` pipe execution
   - `nc` (netcat), `ssh`
   - `cat /etc/...`, `cat ~/.` (sensitive file reads)
3. **Filesystem scope guard** — `find`, `grep`, `ls`, `tree` on `/` or `~` are blocked; agents may only work within the project directory.

## Script Security Scanner

Generated Python scripts are scanned for dangerous patterns before being written to disk:

- `os.system`, `subprocess.*`, `pty.spawn`
- `exec(`, `eval(`, `execfile(`, `compile(`
- `importlib`, `__import__`, `getattr(__`, `__builtins__` (obfuscation vectors)
- `socket.`, `urllib.request`, `http.client` (network exfiltration)
- `shutil.rmtree`, `fs.unlink`, `rm -rf`

Script filenames are sanitized with `path.basename()` to prevent path traversal before write and execute.

---

## Agent Token Budgets

Each agent has a `budgetTokens` limit in its `CAPABILITIES.json`:

```json
{
  "budgetTokens": 100000
}
```

This limits the maximum tokens an agent can consume per request, preventing runaway API costs.

## Agent Tool Restrictions

Each agent's allowed tools are explicitly defined:

```json
{
  "allowedTools": ["delegate_task", "read_file", "search_web", "ask_user"]
}
```

---

## Configuration Security

### Sensitive Files

| File | Contains | Protection |
|---|---|---|
| `.env` | API keys, provider config | In `.gitignore` |
| `dashboard/.env` | Dashboard VITE_API_KEY | Add to `.gitignore` |
| `workspace/gmail_credentials.json` | OAuth client secrets | Never commit |
| `workspace/gmail_token.json` | Gmail access tokens | Never commit |
| `baileys_auth_info/` | WhatsApp session data | Never commit |

::: danger
Never commit API keys, OAuth credentials, or session data to version control.
:::

### `.gitignore` Defaults

```
node_modules/
dist/
.env
dashboard/.env
baileys_auth_info/
workspace/gmail_credentials.json
workspace/gmail_token.json
```

---

## Best Practices

1. **Keep API keys secret** — Never share `DASHBOARD_API_KEY` or `OPENSPIDER_HOOK_TOKEN`. Rotate them if compromised.

2. **Start with allowlists** — Use `allowlist` mode for both DMs and groups. Add trusted contacts individually.

3. **Use mention mode for groups** — In group chats, `mention` mode prevents the agent from responding to every message.

4. **Set token budgets** — Configure reasonable `budgetTokens` in each agent's `CAPABILITIES.json` to prevent excessive API costs.

5. **Rotate API keys regularly** — Update your LLM provider API keys periodically and after any suspected compromise.

6. **Monitor usage** — Use the Dashboard's Usage Analytics tab to track consumption and detect unusual patterns.

7. **Review cron jobs** — Periodically check `workspace/cron_jobs.json` for any unexpected scheduled tasks created by agents.

8. **Keep OpenSpider local** — The dashboard runs on `localhost:4001` by default. If you must expose it externally, use a reverse proxy with TLS and keep the API key secret.

# Security

OpenSpider provides multiple layers of security to control who can interact with your agents and how they behave.

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

This prevents the agent from being noisy in large groups while remaining fully responsive in dedicated channels.

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

The Manager agent has orchestration tools (`delegate_task`), while Worker agents have execution tools (`search_web`, `browse_web`, `send_email`, etc.).

## Cron Job Isolation

Scheduled tasks run in an isolated context:

- **Event suppression**: Agent flow events from cron jobs are **not** broadcast to the dashboard WebSocket
- **Counter tracking**: An `activeCronJobs` counter prevents UI interference
- **Independent agents**: Each cron execution creates a fresh `ManagerAgent` instance

This ensures that background scheduled tasks don't interfere with interactive sessions.

## Configuration Security

### Sensitive Files

| File | Contains | Protection |
|---|---|---|
| `.env` | API keys, provider config | Add to `.gitignore` |
| `workspace/gmail_credentials.json` | OAuth client secrets | Never commit |
| `workspace/gmail_token.json` | Gmail access tokens | Never commit |
| `baileys_auth_info/` | WhatsApp session data | Never commit |

::: danger
Never commit API keys, OAuth credentials, or session data to version control. These are included in `.gitignore` by default.
:::

### `.gitignore` Defaults

The project `.gitignore` includes:

```
node_modules/
dist/
.env
baileys_auth_info/
workspace/gmail_credentials.json
workspace/gmail_token.json
```

## Best Practices

1. **Start with allowlists** — Use `allowlist` mode for both DMs and groups. Add trusted contacts individually.

2. **Use mention mode for groups** — In group chats, `mention` mode prevents the agent from responding to every message. Use `listen` only for dedicated agent groups.

3. **Set token budgets** — Configure reasonable `budgetTokens` in each agent's `CAPABILITIES.json` to prevent excessive API costs.

4. **Rotate API keys regularly** — Update your LLM provider API keys periodically and after any suspected compromise.

5. **Monitor usage** — Use the Dashboard's Usage Analytics tab to track consumption and detect unusual patterns.

6. **Review cron jobs** — Periodically check `workspace/cron_jobs.json` for any unexpected scheduled tasks created by agents.

7. **Secure the dashboard** — The dashboard runs on `localhost:4001` by default. If exposing externally, use a reverse proxy with authentication.

# Agent Configuration

OpenSpider ships with **3 default agents** — Manager, Coder, and Researcher. Each agent's behavior is controlled by a set of **pillar files** in `workspace/agents/<agent-id>/`.

## Default Agents

| Agent | ID | Role | Emoji |
|---|---|---|---|
| **Ananta** | `manager` | Gateway Architect & Manager | 🕷️ |
| **Coder** | `coder` | Code generation & execution | ⚡ |
| **Researcher** | `researcher` | Web research & data gathering | 🔮 |

## Pillar Files

Each agent has 4 pillar files that define its personality, behavior, and capabilities:

### IDENTITY.md

Defines **who** the agent is. When the agent is asked to introduce itself, it references this file.

```markdown
# OpenSpider Manager Agent

You are **Ananta** 🕷️, the core Manager Agent of the OpenSpider multi-agent system.

- **Role**: Gateway Architect & Manager
- **Vibe**: Chill, smart, gets things done.
- **CEO / Boss**: Jane Doe
- **Company**: Acme Corp
- **Website**: https://acme.example.com
- **Capabilities**: Web search, coding, research, email, WhatsApp, scheduling
- **Emoji**: 🕷️
```

::: tip Customize This!
After your first run, edit `workspace/agents/manager/IDENTITY.md` to set your name as CEO/Boss, your company, and website. The agent will use these when introducing itself.
:::

### SOUL.md

Defines **how** the agent behaves — its safety directives, behavioral rules, and system architecture knowledge.

```markdown
# Core Ethos & Safety Directives

1. **Self-Preservation & System Stability**: Never execute commands that could destroy the system.
2. **Delegation Efficiency**: Delegate deep tasks to Sub-Agents.
3. **Truthfulness Over Hallucination**: State clearly when you don't know.
4. **Tool Minimization**: Only use tools necessary for the objective.
5. **Autonomy Limits**: Surface breaking errors instead of infinitely looping.

# System Architecture Knowledge

- **Cron Jobs**: Stored in `workspace/cron_jobs.json`
- **Memory**: Daily logs in `workspace/memory/YYYY-MM-DD.md`
- **Agents**: Configs in `workspace/agents/<agent-id>/`
- **WhatsApp Config**: `workspace/whatsapp_config.json`
- **Skills**: Custom tools in `skills/`
```

::: warning
Modifying SOUL.md can fundamentally change the agent's behavior. Be careful when editing safety directives.
:::

### CAPABILITIES.json

Defines the agent's **tools, role, and operational limits**.

```json
{
    "name": "Ananta",
    "role": "Manager",
    "emoji": "🕷️",
    "color": "fuchsia",
    "allowedTools": ["delegate_task", "read_file", "search_web", "send_email"],
    "maxLoops": 15,
    "status": "running"
}
```

| Field | Type | Description |
|---|---|---|
| `name` | `string` | Display name for the agent |
| `role` | `string` | Agent's role (Manager, Coder, Researcher, or custom) |
| `emoji` | `string` | Emoji shown in the dashboard and chat |
| `color` | `string` | Theme color in the dashboard |
| `allowedTools` | `string[]` | Tools the agent is allowed to use |
| `maxLoops` | `number` | Max iterations in the action loop (prevents runaway) |
| `status` | `"running"` \| `"stopped"` | Agent status (stopped agents show as red in dashboard) |

### USER.md

Stores **learned context** about the user. This file evolves over time as the agent interacts and learns preferences.

```markdown
# User Context

No user preferences or context learned yet.
```

::: info
This file starts empty and is updated by the system as it learns about you. You can also manually add notes here.
:::

## Creating Custom Agents

### Via the Dashboard

1. Go to **Agents Workspace** in the sidebar
2. Click **Create Agent**
3. Fill in name, role, color, and model
4. The system automatically creates all 4 pillar files

### Via the API

```bash
curl -X POST http://localhost:4001/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Analyst",
    "role": "Data Analyst",
    "model": "antigravity",
    "color": "cyan"
  }'
```

### Manually

Create a new directory under `workspace/agents/`:

```bash
mkdir -p workspace/agents/analyst
```

Then create the 4 pillar files (IDENTITY.md, SOUL.md, CAPABILITIES.json, USER.md) following the formats above.

## Workspace Defaults

OpenSpider ships with a `workspace-defaults/` directory that contains the default agent configurations. On **first run**, if no `workspace/` directory exists, the system automatically copies all defaults into `workspace/`.

```
workspace-defaults/
├── agents/
│   ├── manager/
│   │   ├── IDENTITY.md        # Default manager persona
│   │   ├── SOUL.md            # Safety directives + system knowledge
│   │   ├── CAPABILITIES.json  # Tools, role, emoji
│   │   └── USER.md            # Empty user context
│   ├── coder/
│   │   ├── IDENTITY.md
│   │   ├── SOUL.md
│   │   ├── CAPABILITIES.json
│   │   └── USER.md
│   └── researcher/
│       ├── IDENTITY.md
│       ├── SOUL.md
│       ├── CAPABILITIES.json
│       └── USER.md
└── memory.md                  # Long-term memory template
```

::: tip
If you ever want to reset an agent to its defaults, delete its folder from `workspace/agents/` and restart. The defaults will NOT be re-copied (only on first run). To force a reset, delete the entire `workspace/` directory and restart.
:::

## Modifying Agents at Runtime

Agent pillar files (IDENTITY.md, SOUL.md, USER.md) are read at **runtime** — changes take effect immediately without rebuilding. CAPABILITIES.json changes also take effect on the next request.

You can manage agents and edit pillar files natively via the UI:

### Via the Dashboard (Recommended)

1. Navigate to **Agents Workspace** in the left sidebar.
2. Select the agent you want to modify from the list.
3. You will see tabs for each pillar file:
   - **IDENTITY**: Update the agent's core background, title, and persona.
   - **SOUL**: Update the agent's behavior rules and operational constraints.
   - **USER CONTEXT**: Provide the agent with specific information about yourself or the project.
   - **CAPABILITIES**: Add or remove skills, change the underlying AI model, or edit the `name` field to **rename the agent**.
4. Click **Save Changes** to apply the updates immediately.

### Via the API or CLI

- **API**: `PUT /api/agents/:id` with the updated pillar content
- **Manually**: Edit the files directly in `workspace/agents/<id>/` using your text editor

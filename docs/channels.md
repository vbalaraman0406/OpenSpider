# Channels

OpenSpider communicates with users through **WhatsApp** via the [Baileys](https://github.com/WhiskeySockets/Baileys) library. This page covers how to set up and configure the WhatsApp channel.

## Voice Messages 🎤

OpenSpider supports voice-in, voice-out interaction. Users send voice notes which are transcribed locally via Whisper, and agents can reply with ElevenLabs-powered voice notes.

See [Voice Messages](/voice) for full setup and configuration.

## Signal Session Management

OpenSpider automatically manages WhatsApp's end-to-end encryption sessions:

- **Stale session cleanup** — On each startup, all `session-*.json` files in `baileys_auth_info/` are deleted to force fresh E2E negotiation and prevent "Bad MAC" errors
- **Cacheable key store** — Uses `makeCacheableSignalKeyStore` for proper session renegotiation
- **Sent message store** — Caches outgoing message content so Baileys can re-relay messages on retry requests
- **Lock management** — Processing locks are properly released on all early-return paths to prevent message drops

## WhatsApp Setup

### Initial Connection

During onboarding (`openspider onboard`), you'll be prompted to connect WhatsApp by scanning a QR code. If you skipped this step, connect later:

**From a running gateway:**

```bash
openspider channels login
```

This polls the gateway for QR codes and displays them in your terminal. Scan with your phone's WhatsApp.

**Standalone connection:**

```bash
openspider channels whatsapp login
```

Initiates a direct connection without a running gateway.

### Authentication Persistence

After the first scan, authentication credentials are stored in `baileys_auth_info/`. Subsequent starts reconnect automatically — no QR scan needed unless the session is revoked.

::: warning
Don't delete the `baileys_auth_info/` directory unless you want to re-authenticate.
:::

## DM Policies

Control which phone numbers can send direct messages to the agent.

### Allowlist Mode (Default)

Only specified phone numbers can message the agent:

```json
{
  "dmPolicy": "allowlist",
  "allowedDMs": ["14155551234", "447700900000"]
}
```

Phone numbers are stored **without** the `+` prefix.

### Open Mode

Any phone number can message the agent:

```json
{
  "dmPolicy": "open"
}
```

::: caution
Open mode has no access control. Only use this in trusted environments or for testing.
:::

## Group Policies

Control which WhatsApp groups the agent participates in and how it responds.

### Group Allowlist

```json
{
  "groupPolicy": "allowlist",
  "allowedGroups": [
    {
      "jid": "120363423460684848@g.us",
      "mode": "mention"
    },
    {
      "jid": "120363556677889900@g.us",
      "mode": "listen"
    }
  ]
}
```

### Per-Group Modes

Each group can be configured independently:

| Mode | Behavior |
|---|---|
| `mention` | Agent responds **only** when @mentioned in the group |
| `listen` | Agent responds to **every** message in the group |

### Legacy Compatibility

Older configurations used a simple string array for `allowedGroups`:

```json
{
  "allowedGroups": ["120363423460684848@g.us"]
}
```

This format is **automatically migrated** to the object format on load, using the global `botMode` as the default mode for each group.

## Global Bot Mode

The `botMode` field serves as a **fallback** for groups that don't have a per-group mode set:

```json
{
  "botMode": "mention"
}
```

| Value | Behavior |
|---|---|
| `mention` | Default. Agent only responds when @tagged |
| `listen` | Agent responds to all messages in allowed groups |

## Finding Group JIDs

To add a group to your allowlist, you need its JID (WhatsApp group ID). You can find this:

1. **Dashboard** → WhatsApp Security tab → shows connected groups with JIDs
2. **Logs** → Group message events include the group JID

Group JIDs follow the format: `[number]@g.us`

## Configuration via Dashboard

The **WhatsApp Security** tab in the dashboard provides a visual interface for managing:

- DM allowlist (add/remove phone numbers)
- Group allowlist (add/remove groups)
- Per-group mention/listen toggles

Changes made in the dashboard are saved directly to `workspace/whatsapp_config.json`.

See [Dashboard](/dashboard) for more details.

## LID Identity Resolution

WhatsApp has migrated DMs from phone-based JIDs (`1234@s.whatsapp.net`) to LID-based JIDs (`177472511426665@lid`). OpenSpider's firewall handles this seamlessly through a multi-layer resolution system.

### How It Works

When an incoming DM arrives from an `@lid` JID, OpenSpider resolves it through 4 layers:

1. **LID Cache Lookup** — checks `workspace/lid_cache.json` for a known mapping
2. **Config Field Match** — checks if any `allowedDMs` entry has a matching `lid` field
3. **Group Participant Scan** — cross-references the LID against group participant lists
4. **Block + Admin Notify** — if all layers fail, the message is blocked and the admin receives a WhatsApp notification with:
   - The LID number
   - The sender's push name
   - A ready-to-use `map <LID> <PHONE>` command

### Mapping LIDs (3 Methods)

**1. Dashboard UI (recommended)**

Navigate to **Channels → Configure WhatsApp → LID Identity Mappings**. Pending blocked LIDs appear as amber cards. Type the phone number and click **Map**.

**2. WhatsApp Command**

Reply to the bot via WhatsApp DM:

```
map 177472511426665 61423475992
```

The admin (first entry in `allowedDMs`) can send this command. The bot confirms with ✅.

**3. CLI Command**

```bash
openspider lid-map 177472511426665 61423475992
```

Maps the LID to the phone number via the running gateway API.

### LID Configuration Files

| File | Purpose |
|---|---|
| `workspace/lid_cache.json` | Persistent LID→phone mappings |
| `workspace/lid_notified_cache.json` | LIDs already notified to admin (dedup, survives restarts) |
| `workspace/whatsapp_config.json` | `allowedDMs[].lid` field on mapped contacts |

## Email Notification Settings

Configure email delivery for automated outputs and outbound emails.

### Dashboard Configuration

In **Channels → Configure WhatsApp → Email Notification Settings**, set:

| Field | Purpose |
|---|---|
| **Cron Job Results To** | Email address where automated cron job results are delivered |
| **Vendor & Friends To** | Default email address for outbound emails to vendors/contacts |

Leave a field empty to disable that email destination.

Settings are stored in `workspace/email_config.json`.

### API

```bash
# Read current config
curl http://localhost:4001/api/email/config -H "x-api-key: YOUR_KEY"

# Save config
curl -X POST http://localhost:4001/api/email/config \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"cronResultsTo":"admin@example.com","vendorEmailTo":"vendor@example.com"}'
```

## Outbound Message Deduplication ♻️

OpenSpider features a node-wide cryptographic deduplication cache across both the WhatsApp and Gmail pipelines.

When the agent attempts to send multiple identically structured messages to the same exact recipient during a single workflow or interval step (often caused by duplicated prompt delivery rules), the Gateway securely evaluates a SHA-256 rolling hash of the outbound payload. 

Any exact outbound payload duplicates sent within a **10-minute sliding window** are silently suppressed and dropped at the final network mile. This natively protects your WhatsApp and Email inboxes from accidental multi-part bot spam!

## Message Handling Flow

```
Incoming Message
       │
       ▼
  Is it a DM?  ──yes──▸  Check dmPolicy ──▸ allowlist? ──▸ Is sender in allowedDMs?
       │                                                           │
       no                                                    yes / no
       │                                                     │      │
       ▼                                                  Process  Ignore
  Is it a Group?  ──yes──▸  Check groupPolicy ──▸ Is group in allowedGroups?
       │                                                    │
       no (ignore)                                    yes / no
                                                      │      │
                                             Check mode    Ignore
                                                │
                                    ┌───────────┴───────────┐
                                    │                       │
                                 mention                  listen
                                    │                       │
                              Is @mentioned?           Process all
                                 │      │
                              yes      no
                               │        │
                           Process   Ignore
```

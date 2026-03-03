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

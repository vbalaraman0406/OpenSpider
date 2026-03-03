# Troubleshooting

Common issues and solutions when running OpenSpider.

## Installation Issues

### Node.js Version Too Low

**Error:** `Error: OpenSpider requires Node.js version 22 or higher.`

**Fix:** Upgrade Node.js to v22+:

```bash
# Using NVM (recommended)
nvm install 22
nvm use 22
nvm alias default 22

# Verify
node --version
```

---

### `openspider` Command Not Found

**Error:** `zsh: command not found: openspider`

**Fix:** Re-link the CLI:

```bash
cd /path/to/OpenSpider
npm run build:backend
npm link
```

If using NVM, ensure the correct Node version is active before linking.

---

### Build Errors

**Error:** TypeScript compilation fails during `npm run build:backend`

**Fix:**

```bash
# Clear old build artifacts
rm -rf dist/

# Reinstall dependencies
rm -rf node_modules
npm install

# Rebuild
npm run build:backend
```

---

## WhatsApp Issues

### QR Code Not Appearing

**Possible causes:**
1. Gateway not running — Start it with `openspider gateway` or `openspider start`
2. Already authenticated — Check `baileys_auth_info/` exists (means you're already connected)
3. Session expired — Delete `baileys_auth_info/` and restart to get a fresh QR code

```bash
# Force re-authentication
rm -rf baileys_auth_info/
openspider gateway
```

---

### WhatsApp Disconnects Frequently

**Possible causes:**
- Phone has poor internet connectivity
- WhatsApp Web session was closed from the phone
- Multiple WhatsApp Web sessions conflicting

**Fix:**
1. Ensure your phone has a stable internet connection
2. On your phone: WhatsApp → Settings → Linked Devices → verify the session is active
3. Delete `baileys_auth_info/` and re-scan the QR code

---

### Agent Not Responding in Groups

**Check these settings in** `workspace/whatsapp_config.json`:

1. Is the group in `allowedGroups`?
2. Is `groupPolicy` set to `"allowlist"` (default)?
3. Is the group's mode set to `"mention"`? If so, you must @mention the agent
4. For `"listen"` mode, ensure the agent is active and the gateway is running

```bash
# Check current config
cat workspace/whatsapp_config.json
```

---

### Bad MAC Error (Encryption Issues)

**Error:** `Bad MAC` or `Error: Unsupported state or unable to authenticate data` in logs

This occurs when WhatsApp's end-to-end encryption session becomes stale or corrupted after a restart.

**OpenSpider v2.0.0 handles this automatically:**
- Stale session files are cleared on startup
- `makeCacheableSignalKeyStore` enables proper session renegotiation
- Sent messages are cached for Baileys retry re-relay

**If the problem persists:**

```bash
# Force full session reset
rm -rf baileys_auth_info/session-*.json
pm2 restart all
```

::: tip
You do NOT need to delete `creds.json` — only the `session-*.json` files. Your WhatsApp pairing is preserved.
:::

---

### Messages Being Dropped Intermittently

**Symptom:** The first message after restart fails, or messages are silently dropped.

**Possible causes:**
1. Processing lock not properly released — Fixed in v2.0.0 with lock cleanup on all early-return paths
2. Stale encryption sessions — Fixed with automatic session cleanup on startup

**Fix:** Upgrade to v2.0.0 and rebuild:

```bash
npm run build:backend
pm2 restart all
```

---

### Voice Notes Not Working

**Symptom:** Agent doesn't respond with voice, or voice transcription fails.

**Fix:**

1. Verify dependencies are installed:
```bash
which ffmpeg      # Required for audio conversion
which whisper     # Required for transcription
```

2. Check ElevenLabs API key in `voice_config.json` or dashboard (Channels → WhatsApp → Voice Settings)

3. Check server logs for errors:
```bash
pm2 logs openspider-gateway --lines 50
```

See [Voice Messages](/voice) for full setup instructions.

---

## Server Issues

### Port 4001 Already in Use

**Error:** `EADDRINUSE: address already in use :::4001`

**Fix:**

```bash
# Find what's using the port
lsof -i :4001

# Kill the process
kill -9 <PID>

# Or stop existing OpenSpider daemon
openspider stop
```

---

### PM2 Issues

**Problem:** `openspider start` fails or daemon won't start

**Fix:**

```bash
# Check PM2 status
npx pm2 list

# Kill all PM2 processes
npx pm2 kill

# Restart fresh
openspider start
```

---

### Dashboard Not Loading

**Possible causes:**
1. Dashboard not built — Run `cd dashboard && npm run build`
2. Gateway not running — The server serves the dashboard
3. Wrong URL — Ensure you're visiting `http://localhost:4001`

```bash
# Build the dashboard
cd dashboard && npm install && npm run build

# Restart the server
openspider stop && openspider start
```

---

## LLM Provider Issues

### API Key Invalid

**Error:** `Authentication failed` or `Invalid API key`

**Fix:**

1. Check your `.env` file for the correct key variable
2. Verify the key is valid on the provider's website
3. Ensure no extra whitespace or quotes around the key

```bash
# View current model config
openspider models list
```

---

### Model Not Found

**Error:** `Model not found` or `Invalid model`

**Fix:** Update `GEMINI_MODEL` (or the relevant model variable) in `.env` to a valid model name.

Common valid models:

| Provider | Example Models |
|---|---|
| Google Gemini | `gemini-2.5-pro`, `gemini-2.5-flash` |
| Anthropic | `claude-opus-4`, `claude-sonnet-4` |
| OpenAI | `gpt-4o`, `gpt-4-turbo` |
| Ollama | `llama3`, `mistral`, `codellama` |

---

### Ollama Not Connecting

**Error:** Cannot connect to Ollama

**Fix:**
1. Ensure Ollama is running: `ollama serve`
2. Check it's on the default port: `http://localhost:11434`
3. Verify model is downloaded: `ollama list`

---

## Email Issues

### OAuth Setup Fails

**Error:** `OAuth Authentication failed`

**Fix:**
1. Ensure you downloaded the correct JSON (OAuth Client ID, **Desktop** application type)
2. Verify the Gmail API is enabled in your Google Cloud project
3. Try the setup again:

```bash
openspider tools email setup
```

---

### Test Email Not Sending

**Error:** `Test email failed with exit code 1`

**Fix:**
1. Ensure setup was completed: `openspider tools email setup`
2. Verify `workspace/gmail_token.json` exists
3. Check Python 3 is available: `python3 --version`
4. Try resending:

```bash
openspider tools email test --to your@email.com
```

---

## Debugging Tips

### View Live Logs

```bash
# From background daemon
openspider logs

# Or PM2 directly
npx pm2 logs openspider-gateway --lines 200
```

### Check System State

```bash
# Daemon status
npx pm2 list

# Current config
openspider models list

# WhatsApp config
cat workspace/whatsapp_config.json

# Cron jobs
cat workspace/cron_jobs.json
```

### Reset Everything

If all else fails, perform a clean reset:

```bash
# Stop daemon
openspider stop

# Remove generated state (keeps config)
rm -rf baileys_auth_info/
rm -rf dist/

# Rebuild
npm install
npm run build

# Reconfigure
openspider onboard

# Start fresh
openspider start
```

::: tip Need Help?
Check the [GitHub Issues](https://github.com/vbalaraman0406/OpenSpider/issues) page or file a new issue with your error logs.
:::

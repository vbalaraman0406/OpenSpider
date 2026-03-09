# Browser Relay Extension

The **OpenSpider Browser Relay** is a Chrome extension that lets your OpenSpider agents control your real Chrome browser — inheriting all your cookies, sessions, and logged-in accounts.

This is useful when agents need to access authenticated pages (e.g. your Google Drive, Canva, or any site you're already logged into) without needing to re-enter credentials.

## How It Works

Without the extension, agents use a headless Chromium instance (no session, no cookies). With the Browser Relay attached, agents send Chrome DevTools Protocol (CDP) commands directly to your active Chrome tab — so they browse as **you**.

## Installation

### Step 1 — Open Chrome Extensions

Go to `chrome://extensions` in your Chrome browser.

### Step 2 — Enable Developer Mode

Toggle on **Developer mode** in the top-right corner.

### Step 3 — Load the Extension

Click **"Load unpacked"** and select the `chrome-extension/` folder from your OpenSpider directory:

- **Mac / Linux (local):** `~/OpenSpider/chrome-extension`
- **VPS (remote):** You need to have Chrome installed locally and point it to a local copy of the extension folder. Download just the `chrome-extension/` folder from [GitHub](https://github.com/vbalaraman0406/OpenSpider/tree/main/chrome-extension).

The **OpenSpider Browser Relay** icon will appear in your Chrome toolbar.

## Connecting to Your Gateway

1. Click the 🕷️ OpenSpider icon in the Chrome toolbar
2. Fill in the popup:

| Field | Value |
|---|---|
| **Gateway Token** | Your token from `openspider status` (the `Gateway Token:` line) |
| **Relay Port** | `4001` (default) |

3. Click **"Attach to Current Tab"**

The status will show **Connected** when the relay is active.

::: tip Remote VPS Setup
If your OpenSpider is running on a remote VPS, you'll need to expose port `4001` to your local machine via SSH tunnel or Tailscale before the extension can connect:

```bash
# SSH tunnel example
ssh -L 4001:localhost:4001 user@your-vps-ip
```
Then set the Relay Port to `4001` and it will route through the tunnel.
:::

## Using the Extension

Once attached, your agents automatically use the relay for all `browse_web` actions — no changes needed in your prompts.

### Export Cookies

Click the **"Export Cookies to OpenSpider"** button (green) to send your active tab's cookies to the agent context. This is useful for one-off authenticated scraping tasks.

### Detaching

Click **"Detach"** in the popup to disconnect the relay. Agents will fall back to the built-in headless browser.

## Troubleshooting

**"Not connected" after clicking Attach**
- Make sure the OpenSpider gateway is running (`openspider status`)
- Check the Gateway Token matches exactly
- Verify the port (default `4001`) is not blocked by a firewall

**Extension not appearing after loading**
- Make sure Developer Mode is enabled in `chrome://extensions`
- Try clicking "Reload" on the extension card

**Agents still using headless browser**
- The relay only works when the extension is attached (`Connected` status showing)
- Restart the extension popup and re-attach

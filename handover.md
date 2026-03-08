# OpenSpider Agent Handoff Document

## Session Goal
Fix infinite message loops in the WhatsApp integration, specifically focusing on enabling self-chat ("Message Yourself") without breaking the global `botMode="mention"` rule or triggering self-echo loops.

## Work Completed

### 1. Ironclad Loop Prevention
*   **File:** `src/whatsapp.ts`
*   **Action:** Refactored the `fromMe` firewall logic.
*   **Details:** We now drop all echoes *before* any other processing.
    *   `sentMessageIds` cache check (drops exact message IDs we know we sent).
    *   `✨ *` prefix string-match (a fallback sledgehammer that drops *any* message containing the bot's signature, even if the cache clears or whitespace varies).

### 2. Self-Chat (`isNoteToSelf`) Enablement
*   **File:** `src/whatsapp.ts`
*   **Action:** Expanded `isNoteToSelf` logic to recognize secondary devices.
*   **Details:** Previously, messages sent from a Linked Device (WhatsApp Web/Desktop) appeared with `@lid` (Lid JID) instead of the primary phone number, causing the firewall to block them as unauthenticated DMs. We added `msg.key.remoteJid?.includes('@lid')` and exact `myLid` matching so self-chat works globally across all logged-in devices.

### 3. Mention Requirement Bypass for Self-Chat
*   **File:** `src/whatsapp.ts`
*   **Action:** Modified the global `botMode: 'mention'` rule.
*   **Details:** While the bot *requires* an `@Ananta` mention to respond in DMs or Groups, we added an exception for `isNoteToSelf`. The user no longer has to tag the bot when talking to it in their private self-chat space.

### 4. Agent Name Discovery Fix
*   **File:** `src/whatsapp.ts`
*   **Action:** Updated how the bot learns its own name on boot.
*   **Details:** It was defaulting to `OpenSpider` and getting confused. We updated `agentName` discovery to prioritize parsing the `name:` field directly from `workspace/agents/manager/IDENTITY.md` via `PersonaShell.getIdentity()`.

### 5. UI "Forwarded" Icon Removal
*   **File:** `src/whatsapp.ts`
*   **Action:** Cleared `contextInfo` on outgoing WhatsApp messages.
*   **Details:** To stop the white `i` (Forwarded/System) icon from rendering on the bot's replies, we explicitly pass `contextInfo: {}` in text and voice `sock.sendMessage` calls.

### 6. Agent Introduction Prompt (Workspace Defaults)
*   **Files:** `workspace/agents/manager/SOUL.md` & `workspace-defaults/agents/manager/SOUL.md`
*   **Action:** Updated the LLM System Prompt.
*   **Details:** Added a `CRITICAL REQUIREMENT` instructing the agent to *always* end its self-introduction by explaining the invocation method to the user (e.g., "To talk to me, just mention my name like @Ananta!"). 

### 7. Bad MAC & QR Code Re-Authentication
*   **Action:** Purged corrupted Baileys session folder.
*   **Details:** During rapid PM2 reboots while debugging the loop, the local Signal session keys fell out of sync with Meta's servers, resulting in silent `Bad MAC Error` decryption failures. The bot couldn't read inbound messages anymore. We completely deleted the `baileys_auth_info` directory at the project root and had the user re-scan the QR code via `openspider channels login`.

## Current State
*   All fixes have been tested and verified.
*   Code was packaged, committed to Git (`b69d39c` & `6d18a28`), and pushed to `origin/main`.
*   The `openspider-gateway` PM2 background process is running healthy without Bad MAC errors.

### 8. Ubuntu Headless Browser Execution (Puppeteer)
*   **Files:** `src/browser/manager.ts`, `src/browser/config.ts` (and related web research skills)
*   **Action:** Investigated and resolved Chromium/Puppeteer startup crashes on headless Ubuntu servers.
*   **Details:** We identified that Puppeteer fails to launch out-of-the-box on raw Ubuntu server instances without a display server. 
    *   Verified the logic that checks `isUbuntuHeadless` to inject necessary Puppeteer launch arguments (`--no-sandbox`, `--disable-setuid-sandbox`, `--disable-gpu`, `--disable-dev-shm-usage`).
    *   Diagnosed that even with these flags, the browser required proper XVFB (X Virtual Framebuffer) setup or the correct shared library dependencies (`libnss3`, `libx11-xcb1`, `libatk-bridge2.0-0`, etc.) installed on the host machine to render headless DOM.
    *   Determined that when running OpenSpider on a raw Ubuntu droplet/server, the system needs the prerequisite `apt-get install` commands for Puppeteer to function natively without sandboxing errors.
### 9. Next Steps for New Agent Session
*   **Linux Headless Testing:** The new session should pick up the headless Chrome execution testing on the remote Ubuntu server, ensuring the `--no-sandbox` flags interact correctly with the `isUbuntuHeadless` config.
*   **Puppeteer Dependencies:** Verify if an automated `apt-get` setup script is needed in `setup.ts` to pre-install Chromium dependencies (`libgbm1`, `libasound2`, etc.) when deploying OpenSpider to a fresh cloud instance.

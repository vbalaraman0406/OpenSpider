// chrome-extension/popup.js
document.addEventListener('DOMContentLoaded', async () => {
    const hostInput = document.getElementById('host');
    const tokenInput = document.getElementById('token');
    const portInput = document.getElementById('port');
    const toggleBtn = document.getElementById('toggleBtn');
    const cookieBtn = document.getElementById('cookieBtn');
    const statusText = document.getElementById('statusText');

    // Load saved settings
    chrome.storage.local.get(['gatewayHost', 'gatewayToken', 'relayPort'], (result) => {
        if (result.gatewayHost) hostInput.value = result.gatewayHost;
        if (result.gatewayToken) tokenInput.value = result.gatewayToken;
        if (result.relayPort) portInput.value = result.relayPort;
    });

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // Check status
    chrome.runtime.sendMessage({ action: 'status' }, (response) => {
        if (response && response.tabId === tab.id) {
            setAttachedState();
        } else {
            setDetachedState();
        }
    });

    toggleBtn.addEventListener('click', async () => {
        const host = hostInput.value.trim() || '127.0.0.1';
        const token = tokenInput.value;
        const port = parseInt(portInput.value, 10) || 4001;

        // Save settings
        chrome.storage.local.set({ gatewayHost: host, gatewayToken: token, relayPort: port });

        if (toggleBtn.classList.contains('detach')) {
            chrome.runtime.sendMessage({ action: 'detach', tabId: tab.id }, () => {
                setDetachedState();
            });
        } else {
            statusText.innerText = "Connecting...";
            chrome.runtime.sendMessage({ action: 'attach', tabId: tab.id, token, port, host }, (res) => {
                if (res && res.success) {
                    setAttachedState();
                } else {
                    statusText.innerText = "Error requesting attach";
                }
            });
            // Close the popup to let the badge tell the story
            setTimeout(() => window.close(), 1000);
        }
    });

    cookieBtn.addEventListener('click', async () => {
        const host = hostInput.value.trim() || '127.0.0.1';
        const port = parseInt(portInput.value, 10) || 4001;
        const token = tokenInput.value;
        const [currentTab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!currentTab || !currentTab.url) {
            statusText.innerText = "Error: Cannot determine tab URL.";
            return;
        }

        // Save settings
        chrome.storage.local.set({ gatewayHost: host, gatewayToken: token, relayPort: port });

        try {
            statusText.innerText = `Exporting cookies to ${host}:${port}...`;

            // Extract all cookies corresponding to the current tab's URL
            const cookies = await chrome.cookies.getAll({ url: currentTab.url });

            if (cookies.length === 0) {
                statusText.innerText = "No cookies found for this site.";
                return;
            }

            // Remap Chrome cookies to Playwright compatible format
            const playwrightCookies = cookies.map(c => ({
                name: c.name,
                value: c.value,
                domain: c.domain,
                path: c.path,
                secure: c.secure,
                httpOnly: c.httpOnly,
                sameSite: ['unspecified', 'no_restriction'].includes(c.sameSite)
                    ? 'None'
                    : (c.sameSite === 'lax' ? 'Lax' : 'Strict'),
                expires: c.expirationDate || -1
            }));

            // Try HTTPS first, then HTTP (VPS may be behind reverse proxy)
            let response = null;
            const protocols = host === '127.0.0.1' || host === 'localhost'
                ? ['http']
                : ['https', 'http'];

            for (const protocol of protocols) {
                try {
                    response = await fetch(`${protocol}://${host}:${port}/api/v1/browser/cookies`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'x-api-key': token
                        },
                        body: JSON.stringify({ cookies: playwrightCookies })
                    });
                    break; // Success — stop trying protocols
                } catch (e) {
                    console.log(`${protocol} failed, trying next...`, e.message);
                }
            }

            if (!response) {
                throw new Error(`Cannot reach server at ${host}:${port}. Check host, port, and firewall.`);
            }

            if (response.ok) {
                const data = await response.json();
                statusText.innerText = `✅ ${data.count} cookies exported! (${data.persisted} total saved)`;
                statusText.style.color = "#22c55e";
                setTimeout(() => window.close(), 2000);
            } else {
                throw new Error(`Server returned ${response.status}`);
            }
        } catch (error) {
            console.error(error);
            statusText.innerText = `Export failed: ${error.message}`;
            statusText.style.color = "#ef4444";
        }
    });

    function setAttachedState() {
        toggleBtn.textContent = 'Detach from Tab';
        toggleBtn.classList.add('detach');
        statusText.innerText = "Agent can now control this tab.";
    }

    function setDetachedState() {
        toggleBtn.textContent = 'Attach to Current Tab';
        toggleBtn.classList.remove('detach');
        statusText.innerText = "Click to allow agent control.";
    }
});

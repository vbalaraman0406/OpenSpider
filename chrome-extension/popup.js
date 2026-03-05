// chrome-extension/popup.js
document.addEventListener('DOMContentLoaded', async () => {
    const tokenInput = document.getElementById('token');
    const portInput = document.getElementById('port');
    const toggleBtn = document.getElementById('toggleBtn');
    const cookieBtn = document.getElementById('cookieBtn');
    const statusText = document.getElementById('statusText');

    // Load saved settings
    chrome.storage.local.get(['gatewayToken', 'relayPort'], (result) => {
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
        const token = tokenInput.value;
        const port = parseInt(portInput.value, 10) || 4001;

        // Save settings
        chrome.storage.local.set({ gatewayToken: token, relayPort: port });

        if (toggleBtn.classList.contains('detach')) {
            chrome.runtime.sendMessage({ action: 'detach', tabId: tab.id }, () => {
                setDetachedState();
            });
        } else {
            statusText.innerText = "Connecting...";
            chrome.runtime.sendMessage({ action: 'attach', tabId: tab.id, token, port }, (res) => {
                if (res && res.success) {
                    setAttachedState();
                } else {
                    statusText.innerText = "Error requesting attach";
                }
            });
            // We'll close the popup to let let the badge tell the story, or let them see the error
            setTimeout(() => window.close(), 1000);
        }
    });

    cookieBtn.addEventListener('click', async () => {
        const port = parseInt(portInput.value, 10) || 4001;
        const token = tokenInput.value;
        const [currentTab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!currentTab || !currentTab.url) {
            statusText.innerText = "Error: Cannot determine tab URL.";
            return;
        }

        try {
            statusText.innerText = "Exporting cookies...";

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

            // Send to OpenSpider Gateway API (default 4001)
            const apiPort = 4001;
            const response = await fetch(`http://127.0.0.1:${apiPort}/api/v1/browser/cookies`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ cookies: playwrightCookies })
            });

            if (response.ok) {
                statusText.innerText = "✅ Cookies exported successfully!";
                statusText.style.color = "#22c55e";
                setTimeout(() => window.close(), 1500);
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

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

        statusText.innerText = `Exporting cookies to ${host}:${port}...`;
        statusText.style.color = "#666";

        // Delegate cookie export to background service worker to avoid mixed-content blocking.
        // The popup runs in the page's security context (HTTPS), so fetch to HTTP is blocked.
        // The service worker has its own context and can freely make HTTP requests.
        chrome.runtime.sendMessage({
            action: 'exportCookies',
            tabUrl: currentTab.url,
            host,
            port,
            token
        }, (response) => {
            if (chrome.runtime.lastError) {
                statusText.innerText = `Export failed: ${chrome.runtime.lastError.message}`;
                statusText.style.color = "#ef4444";
                return;
            }
            if (response && response.success) {
                statusText.innerText = `✅ ${response.count} cookies exported! (${response.persisted} total saved)`;
                statusText.style.color = "#22c55e";
                setTimeout(() => window.close(), 2000);
            } else {
                statusText.innerText = `Export failed: ${response?.error || 'Unknown error'}`;
                statusText.style.color = "#ef4444";
            }
        });
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

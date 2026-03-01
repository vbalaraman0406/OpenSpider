// chrome-extension/popup.js
document.addEventListener('DOMContentLoaded', async () => {
    const tokenInput = document.getElementById('token');
    const portInput = document.getElementById('port');
    const toggleBtn = document.getElementById('toggleBtn');
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
        const port = parseInt(portInput.value, 10) || 18792;

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

// Comet Browser VCS Extension - Popup Script

class CometVCSPopup {
    constructor() {
        this.init();
        this.bindEvents();
        this.checkVCSStatus();
    }

    init() {
        this.savePageBtn = document.getElementById('save-page-btn');
        this.saveSelectionBtn = document.getElementById('save-selection-btn');
        this.viewHistoryBtn = document.getElementById('view-history-btn');
        this.settingsBtn = document.getElementById('settings-btn');
        this.statusDiv = document.getElementById('status');
        this.statusTitle = document.getElementById('status-title');
        this.statusText = document.getElementById('status-text');
        this.progressFill = document.getElementById('progress-fill');
        this.loadingDiv = document.getElementById('loading');
        this.mainContent = document.getElementById('main-content');
    }

    bindEvents() {
        this.savePageBtn.addEventListener('click', () => this.saveCurrentPage());
        this.saveSelectionBtn.addEventListener('click', () => this.saveSelection());
        this.viewHistoryBtn.addEventListener('click', () => this.viewHistory());
        this.settingsBtn.addEventListener('click', () => this.openSettings());
    }

    async checkVCSStatus() {
        try {
            const response = await this.sendMessage({ action: 'checkStatus' });
            if (response && response.connected) {
                this.showStatus('Connected', 'Hybrid VCS is ready', 'success');
            } else {
                this.showStatus('Disconnected', 'Please start Hybrid VCS server', 'error');
            }
        } catch (error) {
            this.showStatus('Error', 'Unable to connect to VCS', 'error');
        }
    }

    async saveCurrentPage() {
        this.showLoading(true);
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            // Get page content
            const result = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: () => {
                    return {
                        title: document.title,
                        url: window.location.href,
                        content: document.documentElement.outerHTML,
                        textContent: document.body ? document.body.innerText : '',
                        timestamp: new Date().toISOString()
                    };
                }
            });

            const pageData = result[0].result;

            // Save to VCS
            const response = await this.sendMessage({
                action: 'savePage',
                data: pageData
            });

            if (response && response.success) {
                this.showStatus('Success', `Page saved with commit: ${response.commitHash.slice(0, 8)}`, 'success');
                this.showNotification('Page Saved', 'Content has been versioned successfully!');
            } else {
                throw new Error(response?.error || 'Save failed');
            }

        } catch (error) {
            console.error('Save page error:', error);
            this.showStatus('Error', error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async saveSelection() {
        this.showLoading(true);
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            // Get selected text
            const result = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: () => {
                    const selection = window.getSelection();
                    if (!selection.rangeCount) return null;

                    const range = selection.getRangeAt(0);
                    const selectedText = selection.toString();

                    if (!selectedText.trim()) return null;

                    // Get context around selection
                    const container = range.commonAncestorContainer;
                    const element = container.nodeType === Node.TEXT_NODE ? container.parentElement : container;

                    return {
                        text: selectedText,
                        url: window.location.href,
                        title: document.title,
                        context: element.outerHTML || element.textContent,
                        timestamp: new Date().toISOString()
                    };
                }
            });

            const selectionData = result[0].result;

            if (!selectionData) {
                this.showStatus('Warning', 'No text selected', 'error');
                return;
            }

            // Save to VCS
            const response = await this.sendMessage({
                action: 'saveSelection',
                data: selectionData
            });

            if (response && response.success) {
                this.showStatus('Success', `Selection saved with commit: ${response.commitHash.slice(0, 8)}`, 'success');
                this.showNotification('Selection Saved', 'Selected text has been versioned!');
            } else {
                throw new Error(response?.error || 'Save failed');
            }

        } catch (error) {
            console.error('Save selection error:', error);
            this.showStatus('Error', error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async viewHistory() {
        try {
            const response = await this.sendMessage({ action: 'getHistory' });
            if (response && response.history) {
                // Open a new tab with history view
                chrome.tabs.create({
                    url: chrome.runtime.getURL('history.html'),
                    active: true
                });
            }
        } catch (error) {
            this.showStatus('Error', 'Unable to load history', 'error');
        }
    }

    async openSettings() {
        chrome.tabs.create({
            url: chrome.runtime.getURL('settings.html'),
            active: true
        });
    }

    async sendMessage(message) {
        return new Promise((resolve, reject) => {
            chrome.runtime.sendMessage(message, (response) => {
                if (chrome.runtime.lastError) {
                    reject(new Error(chrome.runtime.lastError.message));
                } else {
                    resolve(response);
                }
            });
        });
    }

    showStatus(title, text, type = 'info') {
        this.statusTitle.textContent = title;
        this.statusText.textContent = text;
        this.statusDiv.className = `status ${type}`;
        this.statusDiv.classList.remove('hidden');

        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.statusDiv.classList.add('hidden');
        }, 5000);
    }

    showLoading(show) {
        if (show) {
            this.mainContent.classList.add('hidden');
            this.loadingDiv.classList.remove('hidden');
        } else {
            this.mainContent.classList.remove('hidden');
            this.loadingDiv.classList.add('hidden');
        }
    }

    showNotification(title, message) {
        chrome.notifications.create({
            type: 'basic',
            iconUrl: chrome.runtime.getURL('icons/icon128.png'),
            title: title,
            message: message
        });
    }

    updateProgress(percent) {
        this.progressFill.style.width = `${percent}%`;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CometVCSPopup();
});
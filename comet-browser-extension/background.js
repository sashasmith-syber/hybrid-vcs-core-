// Comet Browser VCS Extension - Background Script (Service Worker)

class CometVCSBackground {
    constructor() {
        this.vcsEndpoint = 'http://localhost:8081';
        this.init();
    }

    init() {
        // Handle extension installation
        chrome.runtime.onInstalled.addListener(this.onInstalled.bind(this));

        // Handle messages from popup and content scripts
        chrome.runtime.onMessage.addListener(this.onMessage.bind(this));

        // Handle keyboard shortcuts
        chrome.commands.onCommand.addListener(this.onCommand.bind(this));

        // Handle context menu clicks
        chrome.contextMenus.onClicked.addListener(this.onContextMenuClick.bind(this));

        console.log('Comet VCS Extension background script loaded');
    }

    onInstalled(details) {
        if (details.reason === 'install') {
            // Create context menu items
            chrome.contextMenus.create({
                id: 'save-page',
                title: 'Save Page to VCS',
                contexts: ['page']
            });

            chrome.contextMenus.create({
                id: 'save-selection',
                title: 'Save Selection to VCS',
                contexts: ['selection']
            });

            chrome.contextMenus.create({
                id: 'save-link',
                title: 'Save Link to VCS',
                contexts: ['link']
            });

            // Set default settings
            chrome.storage.sync.set({
                vcsEndpoint: this.vcsEndpoint,
                autoSave: false,
                compressionLevel: 6,
                maxFileSize: 10 * 1024 * 1024 // 10MB
            });
        }
    }

    async onMessage(message, sender, sendResponse) {
        try {
            switch (message.action) {
                case 'checkStatus':
                    sendResponse(await this.checkVCSStatus());
                    break;

                case 'savePage':
                    sendResponse(await this.savePage(message.data));
                    break;

                case 'saveSelection':
                    sendResponse(await this.saveSelection(message.data));
                    break;

                case 'getHistory':
                    sendResponse(await this.getHistory());
                    break;

                case 'getVersions':
                    sendResponse(await this.getVersions(message.commitHash));
                    break;

                default:
                    sendResponse({ error: 'Unknown action' });
            }
        } catch (error) {
            console.error('Background message error:', error);
            sendResponse({ error: error.message });
        }

        return true; // Keep message channel open for async response
    }

    onCommand(command) {
        switch (command) {
            case 'save-page':
                this.saveCurrentPage();
                break;
            case 'version-selection':
                this.saveCurrentSelection();
                break;
        }
    }

    onContextMenuClick(info, tab) {
        // Check if we're on a restricted page (chrome://, file://, etc.)
        if (tab.url && (tab.url.startsWith('chrome://') ||
                       tab.url.startsWith('chrome-extension://') ||
                       tab.url.startsWith('file://') ||
                       tab.url.startsWith('about:'))) {
            console.warn('Context menu action blocked on restricted page:', tab.url);
            return;
        }

        switch (info.menuItemId) {
            case 'save-page':
                this.savePageFromTab(tab);
                break;
            case 'save-selection':
                this.saveSelectionFromInfo(info, tab);
                break;
            case 'save-link':
                this.saveLink(info, tab);
                break;
        }
    }

    async checkVCSStatus() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

            const response = await fetch(`${this.vcsEndpoint}/health`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                return { connected: true, status: 'healthy' };
            } else {
                return { connected: false, status: 'unhealthy' };
            }
        } catch (error) {
            console.error('VCS status check failed:', error);
            if (error.name === 'AbortError') {
                return { connected: false, error: 'Connection timeout (5s)' };
            }
            return { connected: false, error: error.message };
        }
    }

    async savePage(pageData) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

            const response = await fetch(`${this.vcsEndpoint}/api/save-page`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                signal: controller.signal,
                body: JSON.stringify({
                    title: pageData.title,
                    url: pageData.url,
                    content: pageData.content,
                    textContent: pageData.textContent,
                    timestamp: pageData.timestamp,
                    metadata: {
                        userAgent: navigator.userAgent,
                        viewport: { width: window.innerWidth, height: window.innerHeight },
                        referrer: document.referrer
                    }
                })
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return {
                success: true,
                commitHash: result.commit_hash,
                message: 'Page saved successfully'
            };

        } catch (error) {
            console.error('Save page error:', error);
            throw new Error(`Failed to save page: ${error.message}`);
        }
    }

    async saveSelection(selectionData) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

            const response = await fetch(`${this.vcsEndpoint}/api/save-selection`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                signal: controller.signal,
                body: JSON.stringify({
                    text: selectionData.text,
                    url: selectionData.url,
                    title: selectionData.title,
                    context: selectionData.context,
                    timestamp: selectionData.timestamp,
                    metadata: {
                        selectionLength: selectionData.text.length,
                        contextType: 'text'
                    }
                })
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return {
                success: true,
                commitHash: result.commit_hash,
                message: 'Selection saved successfully'
            };

        } catch (error) {
            console.error('Save selection error:', error);
            throw new Error(`Failed to save selection: ${error.message}`);
        }
    }

    async getHistory() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 second timeout

            const response = await fetch(`${this.vcsEndpoint}/api/history`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return {
                success: true,
                history: result.history
            };

        } catch (error) {
            console.error('Get history error:', error);
            throw new Error(`Failed to get history: ${error.message}`);
        }
    }

    async getVersions(commitHash) {
        try {
            const response = await fetch(`${this.vcsEndpoint}/api/versions/${commitHash}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return {
                success: true,
                versions: result.versions
            };

        } catch (error) {
            console.error('Get versions error:', error);
            throw new Error(`Failed to get versions: ${error.message}`);
        }
    }

    async saveCurrentPage() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            await this.savePageFromTab(tab);
        } catch (error) {
            console.error('Save current page error:', error);
        }
    }

    async saveCurrentSelection() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            const result = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: () => {
                    const selection = window.getSelection();
                    return selection.toString().trim();
                }
            });

            if (result[0].result) {
                // Save the selection
                const selectionData = {
                    text: result[0].result,
                    url: tab.url,
                    title: tab.title,
                    timestamp: new Date().toISOString()
                };

                await this.saveSelection(selectionData);

                // Show notification
                chrome.notifications.create({
                    type: 'basic',
                    iconUrl: chrome.runtime.getURL('icons/icon128.png'),
                    title: 'Selection Saved',
                    message: 'Selected text has been versioned to VCS'
                });
            }
        } catch (error) {
            console.error('Save current selection error:', error);
        }
    }

    async savePageFromTab(tab) {
        try {
            const result = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: () => {
                    const content = document.documentElement.outerHTML;
                    const textContent = document.body ? document.body.innerText : '';

                    // Check for excessively large content (memory safety)
                    const MAX_CONTENT_SIZE = 50 * 1024 * 1024; // 50MB limit
                    if (content.length > MAX_CONTENT_SIZE) {
                        console.warn('Page content too large, truncating:', content.length);
                        return {
                            title: document.title,
                            url: window.location.href,
                            content: content.substring(0, MAX_CONTENT_SIZE) + '<!-- CONTENT TRUNCATED -->',
                            textContent: textContent.substring(0, 1024 * 1024), // 1MB text limit
                            timestamp: new Date().toISOString(),
                            truncated: true
                        };
                    }

                    return {
                        title: document.title,
                        url: window.location.href,
                        content: content,
                        textContent: textContent,
                        timestamp: new Date().toISOString()
                    };
                }
            });

            await this.savePage(result[0].result);

            chrome.notifications.create({
                type: 'basic',
                iconUrl: chrome.runtime.getURL('icons/icon128.png'),
                title: 'Page Saved',
                message: `${tab.title} has been versioned to VCS`
            });

        } catch (error) {
            console.error('Save page from tab error:', error);
        }
    }

    async saveSelectionFromInfo(info, tab) {
        try {
            const selectionData = {
                text: info.selectionText,
                url: info.pageUrl,
                title: tab.title,
                timestamp: new Date().toISOString()
            };

            await this.saveSelection(selectionData);

            chrome.notifications.create({
                type: 'basic',
                iconUrl: chrome.runtime.getURL('icons/icon128.png'),
                title: 'Selection Saved',
                message: 'Selected text has been versioned to VCS'
            });

        } catch (error) {
            console.error('Save selection from info error:', error);
        }
    }

    async saveLink(info, tab) {
        try {
            const linkData = {
                url: info.linkUrl,
                pageUrl: info.pageUrl,
                title: tab.title || 'Link',
                text: info.linkUrl,
                timestamp: new Date().toISOString(),
                type: 'link'
            };

            const response = await fetch(`${this.vcsEndpoint}/api/save-link`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(linkData)
            });

            if (response.ok) {
                chrome.notifications.create({
                    type: 'basic',
                    iconUrl: chrome.runtime.getURL('icons/icon128.png'),
                    title: 'Link Saved',
                    message: 'Link has been versioned to VCS'
                });
            }

        } catch (error) {
            console.error('Save link error:', error);
        }
    }
}

// Initialize the background script
new CometVCSBackground();
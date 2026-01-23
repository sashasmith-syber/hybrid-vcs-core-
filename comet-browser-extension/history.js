// Comet Browser VCS Extension - History Page

class CometVCSHistory {
    constructor() {
        this.historyData = [];
        this.filteredData = [];
        this.currentFilter = 'all';
        this.searchTerm = '';

        this.init();
        this.loadHistory();
    }

    init() {
        this.searchInput = document.getElementById('search-input');
        this.historyContainer = document.getElementById('history-container');
        this.loadingDiv = document.getElementById('loading');
        this.errorDiv = document.getElementById('error');
        this.emptyState = document.getElementById('empty-state');
        this.refreshBtn = document.getElementById('refresh-btn');
        this.backBtn = document.getElementById('back-btn');

        // Bind events
        this.searchInput.addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.applyFilters();
        });

        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentFilter = btn.dataset.filter;
                this.applyFilters();
            });
        });

        this.refreshBtn.addEventListener('click', () => this.loadHistory());
        this.backBtn.addEventListener('click', () => window.close());
    }

    async loadHistory() {
        this.showLoading(true);
        this.hideError();

        try {
            const response = await this.sendMessage({ action: 'getHistory' });

            if (response && response.success) {
                this.historyData = response.history || [];
                this.applyFilters();
            } else {
                throw new Error(response?.error || 'Failed to load history');
            }

        } catch (error) {
            console.error('Load history error:', error);
            this.showError();
        } finally {
            this.showLoading(false);
        }
    }

    applyFilters() {
        this.filteredData = this.historyData.filter(item => {
            // Type filter
            if (this.currentFilter !== 'all' && item.type !== this.currentFilter) {
                return false;
            }

            // Search filter
            if (this.searchTerm) {
                const searchText = `${item.title} ${item.url} ${item.data?.text || ''}`.toLowerCase();
                return searchText.includes(this.searchTerm);
            }

            return true;
        });

        this.renderHistory();
    }

    renderHistory() {
        if (this.filteredData.length === 0) {
            this.showEmptyState(true);
            this.historyContainer.classList.add('hidden');
            return;
        }

        this.showEmptyState(false);
        this.historyContainer.classList.remove('hidden');

        const html = this.filteredData.map(item => this.createHistoryItemHTML(item)).join('');
        this.historyContainer.innerHTML = html;

        // Add click handlers
        this.historyContainer.querySelectorAll('.history-item').forEach((item, index) => {
            item.addEventListener('click', () => this.showItemDetails(this.filteredData[index]));
        });
    }

    createHistoryItemHTML(item) {
        const typeClass = `type-${item.type}`;
        const timestamp = new Date(item.timestamp).toLocaleString();
        const shortCommit = item.commit_hash ? item.commit_hash.substring(0, 8) : '';

        let contentPreview = '';
        let title = item.title || 'Untitled';

        if (item.type === 'webpage') {
            contentPreview = item.data?.textContent?.substring(0, 150) + '...' || 'Webpage content';
        } else if (item.type === 'selection') {
            contentPreview = item.data?.text || 'Text selection';
            title = title || 'Text Selection';
        } else if (item.type === 'link') {
            contentPreview = item.data?.text || item.data?.url || 'Link';
            title = title || 'Link';
        }

        return `
            <div class="history-item" data-id="${item.id}">
                <div class="item-header">
                    <div class="item-title">${this.escapeHtml(title)}</div>
                    <span class="item-type ${typeClass}">${item.type}</span>
                </div>
                ${item.url ? `<div class="item-url">${this.escapeHtml(item.url)}</div>` : ''}
                <div class="item-content">${this.escapeHtml(contentPreview)}</div>
                <div class="item-footer">
                    <span class="item-timestamp">${timestamp}</span>
                    ${shortCommit ? `<span class="item-commit">${shortCommit}</span>` : ''}
                </div>
            </div>
        `;
    }

    showItemDetails(item) {
        // Create a detailed view modal/popup
        const detailsHTML = this.createItemDetailsHTML(item);
        this.showModal(detailsHTML);
    }

    createItemDetailsHTML(item) {
        const timestamp = new Date(item.timestamp).toLocaleDateString() + ' ' +
                         new Date(item.timestamp).toLocaleTimeString();

        let content = '';

        if (item.type === 'webpage') {
            content = `
                <h4>Webpage Details</h4>
                <p><strong>Title:</strong> ${this.escapeHtml(item.title || 'Untitled')}</p>
                <p><strong>URL:</strong> <a href="${item.url}" target="_blank">${this.escapeHtml(item.url)}</a></p>
                <p><strong>Description:</strong> ${this.escapeHtml(item.data?.metadata?.description || 'N/A')}</p>
                <p><strong>Links:</strong> ${item.data?.metadata?.links_count || 0}</p>
                <p><strong>Images:</strong> ${item.data?.metadata?.images_count || 0}</p>
                <div class="content-preview">
                    <strong>Content Preview:</strong><br>
                    <div style="max-height: 200px; overflow-y: auto; background: rgba(0,0,0,0.1); padding: 10px; border-radius: 4px; margin-top: 5px;">
                        ${this.escapeHtml(item.data?.textContent?.substring(0, 500) || 'No content')}${item.data?.textContent?.length > 500 ? '...' : ''}
                    </div>
                </div>
            `;
        } else if (item.type === 'selection') {
            content = `
                <h4>Text Selection Details</h4>
                <p><strong>Page:</strong> ${this.escapeHtml(item.title || 'Untitled')}</p>
                <p><strong>URL:</strong> <a href="${item.url}" target="_blank">${this.escapeHtml(item.url)}</a></p>
                <p><strong>Length:</strong> ${item.data?.metadata?.length || 0} characters</p>
                <div class="content-preview">
                    <strong>Selected Text:</strong><br>
                    <div style="max-height: 200px; overflow-y: auto; background: rgba(0,0,0,0.1); padding: 10px; border-radius: 4px; margin-top: 5px; font-style: italic;">
                        ${this.escapeHtml(item.data?.text || 'No text')}
                    </div>
                </div>
            `;
        } else if (item.type === 'link') {
            content = `
                <h4>Link Details</h4>
                <p><strong>Text:</strong> ${this.escapeHtml(item.data?.text || 'N/A')}</p>
                <p><strong>URL:</strong> <a href="${item.data?.url}" target="_blank">${this.escapeHtml(item.data?.url)}</a></p>
                <p><strong>Page URL:</strong> <a href="${item.url}" target="_blank">${this.escapeHtml(item.url)}</a></p>
            `;
        }

        return `
            <div class="item-details">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #667eea;">${this.escapeHtml(item.title || 'Item Details')}</h3>
                    <span class="item-type type-${item.type}" style="font-size: 11px;">${item.type}</span>
                </div>
                <div style="margin-bottom: 15px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 6px; font-size: 12px;">
                    <strong>Timestamp:</strong> ${timestamp}<br>
                    ${item.commit_hash ? `<strong>Commit:</strong> <code style="background: rgba(0,0,0,0.2); padding: 2px 4px; border-radius: 3px;">${item.commit_hash}</code>` : ''}
                </div>
                ${content}
                <div style="margin-top: 20px; text-align: right;">
                    <button onclick="this.closest('.modal').remove()" style="padding: 8px 16px; background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); border-radius: 4px; color: white; cursor: pointer;">Close</button>
                </div>
            </div>
        `;
    }

    showModal(content) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;

        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        `;

        modalContent.innerHTML = content;
        modal.appendChild(modalContent);

        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        document.body.appendChild(modal);
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

    showLoading(show) {
        if (show) {
            this.loadingDiv.classList.remove('hidden');
            this.historyContainer.classList.add('hidden');
        } else {
            this.loadingDiv.classList.add('hidden');
        }
    }

    showError() {
        this.errorDiv.classList.remove('hidden');
        this.historyContainer.classList.add('hidden');
        this.emptyState.classList.add('hidden');
    }

    hideError() {
        this.errorDiv.classList.add('hidden');
    }

    showEmptyState(show) {
        if (show) {
            this.emptyState.classList.remove('hidden');
        } else {
            this.emptyState.classList.add('hidden');
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CometVCSHistory();
});
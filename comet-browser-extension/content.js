// Comet Browser VCS Extension - Content Script

class CometVCSContent {
    constructor() {
        this.init();
    }

    init() {
        // Listen for messages from background script
        chrome.runtime.onMessage.addListener(this.onMessage.bind(this));

        // Add visual indicators for VCS-enabled content
        this.addVCSIndicators();

        // Track user interactions for potential versioning
        this.trackInteractions();

        console.log('Comet VCS content script loaded');
    }

    onMessage(message, sender, sendResponse) {
        try {
            switch (message.action) {
                case 'getPageContent':
                    sendResponse(this.getPageContent());
                    break;

                case 'getSelectedContent':
                    sendResponse(this.getSelectedContent());
                    break;

                case 'highlightSelection':
                    this.highlightSelection();
                    sendResponse({ success: true });
                    break;

                case 'scrollToElement':
                    this.scrollToElement(message.selector);
                    sendResponse({ success: true });
                    break;

                default:
                    sendResponse({ error: 'Unknown action' });
            }
        } catch (error) {
            console.error('Content script error:', error);
            sendResponse({ error: error.message });
        }

        return true;
    }

    getPageContent() {
        // Extract comprehensive page data
        const pageData = {
            title: document.title,
            url: window.location.href,
            canonicalUrl: this.getCanonicalUrl(),
            description: this.getMetaDescription(),
            keywords: this.getMetaKeywords(),
            author: this.getMetaAuthor(),
            content: document.documentElement.outerHTML,
            textContent: document.body ? document.body.innerText : '',
            readableContent: this.extractReadableContent(),
            links: this.extractLinks(),
            images: this.extractImages(),
            timestamp: new Date().toISOString(),
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            scrollPosition: {
                x: window.pageXOffset,
                y: window.pageYOffset
            },
            userAgent: navigator.userAgent,
            referrer: document.referrer,
            language: document.documentElement.lang || navigator.language,
            charset: document.characterSet,
            lastModified: document.lastModified
        };

        return pageData;
    }

    getSelectedContent() {
        const selection = window.getSelection();
        if (!selection.rangeCount) return null;

        const range = selection.getRangeAt(0);
        const selectedText = selection.toString().trim();

        if (!selectedText) return null;

        // Get context around selection
        const container = range.commonAncestorContainer;
        const element = container.nodeType === Node.TEXT_NODE ? container.parentElement : container;

        // Get bounding rectangle for visual feedback
        const rect = range.getBoundingClientRect();

        return {
            text: selectedText,
            html: this.getSelectionHTML(range),
            context: element.outerHTML || element.textContent,
            xpath: this.getXPath(element),
            cssSelector: this.getCSSSelector(element),
            boundingRect: {
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height
            },
            url: window.location.href,
            title: document.title,
            timestamp: new Date().toISOString()
        };
    }

    getCanonicalUrl() {
        const canonical = document.querySelector('link[rel="canonical"]');
        return canonical ? canonical.href : window.location.href;
    }

    getMetaDescription() {
        const meta = document.querySelector('meta[name="description"]');
        return meta ? meta.getAttribute('content') : '';
    }

    getMetaKeywords() {
        const meta = document.querySelector('meta[name="keywords"]');
        return meta ? meta.getAttribute('content') : '';
    }

    getMetaAuthor() {
        const meta = document.querySelector('meta[name="author"]');
        return meta ? meta.getAttribute('content') : '';
    }

    extractReadableContent() {
        // Simple readable content extraction
        const article = document.querySelector('article') ||
                       document.querySelector('[role="main"]') ||
                       document.querySelector('.content') ||
                       document.body;

        if (!article) return document.body.innerText;

        // Remove scripts, styles, and other non-content elements
        const clone = article.cloneNode(true);
        const elementsToRemove = clone.querySelectorAll('script, style, nav, header, footer, aside, .ads, .advertisement');
        elementsToRemove.forEach(el => el.remove());

        return clone.textContent || clone.innerText || '';
    }

    extractLinks() {
        const links = Array.from(document.querySelectorAll('a[href]')).map(link => ({
            text: link.textContent.trim(),
            href: link.href,
            title: link.title || '',
            rel: link.rel || '',
            target: link.target || '',
            xpath: this.getXPath(link),
            visible: this.isElementVisible(link)
        }));

        return links.filter(link => link.text && link.href);
    }

    extractImages() {
        const images = Array.from(document.querySelectorAll('img[src]')).map(img => ({
            src: img.src,
            alt: img.alt || '',
            title: img.title || '',
            width: img.naturalWidth || img.width,
            height: img.naturalHeight || img.height,
            xpath: this.getXPath(img),
            visible: this.isElementVisible(img)
        }));

        return images.filter(img => img.src);
    }

    getSelectionHTML(range) {
        const clonedSelection = range.cloneContents();
        const div = document.createElement('div');
        div.appendChild(clonedSelection);
        return div.innerHTML;
    }

    getXPath(element) {
        if (element.id) {
            return `//*[@id="${element.id}"]`;
        }

        if (element.className) {
            return `//${element.tagName.toLowerCase()}[contains(@class, "${element.className}")]`;
        }

        const path = [];
        while (element.nodeType === Node.ELEMENT_NODE) {
            let selector = element.nodeName.toLowerCase();
            if (element.id) {
                selector += `#${element.id}`;
                path.unshift(selector);
                break;
            } else {
                let sibling = element.previousSibling;
                let nth = 1;
                while (sibling) {
                    if (sibling.nodeType === Node.ELEMENT_NODE &&
                        sibling.nodeName.toLowerCase() === selector) {
                        nth++;
                    }
                    sibling = sibling.previousSibling;
                }

                if (nth !== 1) {
                    selector += `:nth-child(${nth})`;
                }
            }

            path.unshift(selector);
            element = element.parentNode;
        }

        return path.length ? '/' + path.join('/') : '';
    }

    getCSSSelector(element) {
        const path = [];
        while (element.nodeType === Node.ELEMENT_NODE) {
            let selector = element.nodeName.toLowerCase();

            if (element.id) {
                selector = `#${element.id}`;
                path.unshift(selector);
                break;
            } else if (element.className) {
                selector += `.${element.className.split(' ').join('.')}`;
            } else {
                let sibling = element.previousSibling;
                let nth = 1;
                while (sibling) {
                    if (sibling.nodeType === Node.ELEMENT_NODE &&
                        sibling.nodeName.toLowerCase() === selector) {
                        nth++;
                    }
                    sibling = sibling.previousSibling;
                }

                if (nth !== 1) {
                    selector += `:nth-child(${nth})`;
                }
            }

            path.unshift(selector);
            element = element.parentNode;
        }

        return path.join(' > ');
    }

    isElementVisible(element) {
        const rect = element.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0 &&
               rect.top >= 0 && rect.left >= 0 &&
               rect.bottom <= window.innerHeight &&
               rect.right <= window.innerWidth;
    }

    addVCSIndicators() {
        // Add a subtle indicator that VCS is active on this page
        const indicator = document.createElement('div');
        indicator.id = 'comet-vcs-indicator';
        indicator.innerHTML = `
            <style>
                #comet-vcs-indicator {
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    z-index: 9999;
                    background: rgba(102, 126, 234, 0.9);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    cursor: pointer;
                    opacity: 0.7;
                    transition: opacity 0.3s ease;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                }
                #comet-vcs-indicator:hover {
                    opacity: 1;
                }
                #comet-vcs-indicator::before {
                    content: '☄️';
                    margin-right: 4px;
                }
            </style>
            VCS Active
        `;

        // Click to open extension popup
        indicator.addEventListener('click', () => {
            chrome.runtime.sendMessage({ action: 'openPopup' });
        });

        document.body.appendChild(indicator);

        // Hide indicator after 3 seconds
        setTimeout(() => {
            indicator.style.opacity = '0';
            setTimeout(() => indicator.remove(), 300);
        }, 3000);
    }

    trackInteractions() {
        // Track user interactions that might be worth versioning
        let interactionCount = 0;
        const maxInteractions = 10;

        const trackInteraction = (type, data) => {
            interactionCount++;
            if (interactionCount <= maxInteractions) {
                chrome.runtime.sendMessage({
                    action: 'trackInteraction',
                    type: type,
                    data: data,
                    timestamp: new Date().toISOString()
                });
            }
        };

        // Track text selection
        document.addEventListener('selectionchange', () => {
            const selection = window.getSelection();
            if (selection.toString().trim().length > 50) {
                trackInteraction('selection', {
                    text: selection.toString().substring(0, 200) + '...',
                    length: selection.toString().length
                });
            }
        });

        // Track form interactions
        document.addEventListener('input', (e) => {
            if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') {
                trackInteraction('form_input', {
                    tagName: e.target.tagName,
                    type: e.target.type,
                    value: e.target.value.substring(0, 100)
                });
            }
        });

        // Track clicks on important elements
        document.addEventListener('click', (e) => {
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                const link = e.target.tagName === 'A' ? e.target : e.target.closest('a');
                trackInteraction('link_click', {
                    href: link.href,
                    text: link.textContent.trim()
                });
            }
        });
    }

    highlightSelection() {
        const selection = window.getSelection();
        if (!selection.rangeCount) return;

        const range = selection.getRangeAt(0);
        const highlight = document.createElement('span');
        highlight.style.backgroundColor = 'rgba(102, 126, 234, 0.3)';
        highlight.style.borderRadius = '2px';
        highlight.style.padding = '2px';

        try {
            range.surroundContents(highlight);
        } catch (e) {
            // Fallback for complex selections
            const contents = range.extractContents();
            highlight.appendChild(contents);
            range.insertNode(highlight);
        }

        // Remove highlight after 2 seconds
        setTimeout(() => {
            const parent = highlight.parentNode;
            if (parent) {
                while (highlight.firstChild) {
                    parent.insertBefore(highlight.firstChild, highlight);
                }
                parent.removeChild(highlight);
            }
        }, 2000);
    }

    scrollToElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Add temporary highlight
            element.style.transition = 'background-color 0.3s ease';
            const originalBg = element.style.backgroundColor;
            element.style.backgroundColor = 'rgba(102, 126, 234, 0.3)';
            setTimeout(() => {
                element.style.backgroundColor = originalBg;
            }, 2000);
        }
    }
}

// Initialize content script
new CometVCSContent();
# Comet Browser VCS Extension

A powerful browser extension that integrates with the Hybrid VCS system to enable web content versioning directly from your browser.

## Features

- 🌐 **Save Entire Pages**: Version complete web pages with all content, metadata, and links
- 📝 **Save Text Selections**: Version selected text with context and metadata
- 🔗 **Save Links**: Version URLs and link information
- ⌨️ **Keyboard Shortcuts**: Quick save with `Ctrl+Shift+S` (page) and `Ctrl+Shift+V` (selection)
- 📱 **Context Menus**: Right-click to save content from any webpage
- 📊 **Visual Indicators**: Subtle VCS active indicators on web pages
- 🔄 **Real-time Sync**: Automatic synchronization with Hybrid VCS backend
- 🎨 **Modern UI**: Beautiful gradient interface with smooth animations

## Installation

### Prerequisites

1. **Hybrid VCS Backend**: Ensure the Hybrid VCS server is running on `http://localhost:8080`
   ```bash
   cd ../  # Go to hybrid-vcs-project root
   python -m hybrid_vcs.cli init
   python -m hybrid_vcs.cli serve  # If available, or use your preferred server
   ```

2. **Python Dependencies** (for icon generation):
   ```bash
   pip install Pillow  # For fallback icon generation
   ```

### Chrome Extension Setup

1. **Generate Icons**:
   ```bash
   cd comet-browser-extension
   python generate_icons.py
   ```

   If you don't have image conversion tools, the script will create simple fallback icons.

2. **Load Extension in Chrome**:
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the `comet-browser-extension` folder
   - The extension should now appear in your extensions list

3. **Verify Installation**:
   - You should see the Comet VCS icon (☄️) in your Chrome toolbar
   - Click it to open the extension popup

## Usage

### Basic Operations

1. **Save Current Page**:
   - Click the Comet VCS icon in toolbar
   - Click "💾 Save Current Page"
   - Or use keyboard shortcut: `Ctrl+Shift+S`

2. **Save Text Selection**:
   - Select text on any webpage
   - Click the Comet VCS icon
   - Click "📝 Save Selection"
   - Or use keyboard shortcut: `Ctrl+Shift+V`

3. **Context Menu Options**:
   - Right-click on any webpage → "Save Page to VCS"
   - Right-click on selected text → "Save Selection to VCS"
   - Right-click on links → "Save Link to VCS"

### Advanced Features

- **Automatic Content Detection**: The extension intelligently extracts readable content, metadata, and structured data
- **Link Analysis**: Captures all links on a page with visibility and context information
- **Image Metadata**: Extracts image information including dimensions and alt text
- **User Interaction Tracking**: Monitors selections and form inputs for potential versioning

## Configuration

### Extension Settings

Access settings through the extension popup:
- **VCS Endpoint**: Configure the Hybrid VCS server URL (default: `http://localhost:8080`)
- **Auto-save**: Automatically save pages on certain triggers
- **Compression Level**: Set Zstandard compression level for content
- **Max File Size**: Limit maximum content size for versioning

### Keyboard Shortcuts

- `Ctrl+Shift+S` / `Cmd+Shift+S`: Save current page
- `Ctrl+Shift+V` / `Cmd+Shift+V`: Save current text selection

## API Integration

The extension communicates with the Hybrid VCS backend via REST API:

### Endpoints Used

- `GET /health` - Check VCS server status
- `POST /api/save-page` - Save complete page content
- `POST /api/save-selection` - Save text selection
- `POST /api/save-link` - Save link information
- `GET /api/history` - Retrieve version history

### Data Structures

**Page Save Request**:
```json
{
  "title": "Page Title",
  "url": "https://example.com",
  "content": "<html>...</html>",
  "textContent": "Readable text...",
  "metadata": {
    "userAgent": "Mozilla/5.0...",
    "viewport": {"width": 1920, "height": 1080},
    "links": [...],
    "images": [...]
  }
}
```

**Selection Save Request**:
```json
{
  "text": "Selected text content",
  "url": "https://example.com",
  "title": "Page Title",
  "context": "Surrounding HTML context",
  "xpath": "//div[@class='content']/p[3]",
  "boundingRect": {"x": 100, "y": 200, "width": 300, "height": 50}
}
```

## Development

### Project Structure

```
comet-browser-extension/
├── manifest.json          # Extension manifest
├── popup.html            # Extension popup UI
├── popup.js              # Popup logic
├── background.js         # Background service worker
├── content.js            # Content script for web pages
├── icons/                # Extension icons
│   ├── icon.svg          # Source SVG icon
│   └── icon{16,32,48,128}.png  # Generated PNG icons
├── generate_icons.py     # Icon generation script
└── README.md            # This file
```

### Building from Source

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd comet-browser-extension
   ```

2. **Generate icons**:
   ```bash
   python generate_icons.py
   ```

3. **Load in browser**:
   - Follow the installation steps above

### Development Tips

- Use Chrome DevTools to debug the extension
- Check `chrome://extensions/` for console logs
- Test with different websites and content types
- Monitor network requests to ensure API communication

## Browser Compatibility

- ✅ **Chrome**: Full support (primary target)
- ✅ **Edge**: Should work (Chromium-based)
- ✅ **Opera**: Should work (Chromium-based)
- ❌ **Firefox**: Requires manifest v2 adaptation
- ❌ **Safari**: Requires significant modifications

## Troubleshooting

### Common Issues

1. **"VCS server not connected"**
   - Ensure Hybrid VCS backend is running on localhost:8080
   - Check firewall settings
   - Verify CORS configuration

2. **Extension not loading**
   - Verify all icon files exist
   - Check manifest.json for syntax errors
   - Try reloading the extension

3. **Save operations failing**
   - Check browser console for error messages
   - Verify API endpoints are accessible
   - Check network connectivity

### Debug Mode

Enable verbose logging in Chrome DevTools:
1. Open extension popup
2. Right-click → Inspect popup
3. Check Console tab for detailed logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly across different websites
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: Report bugs and request features
- **Discussions**: Share ideas and ask questions
- **Documentation**: Check this README and inline code comments

---

**Made with ☄️ for the future of web content versioning**
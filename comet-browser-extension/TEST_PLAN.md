# Comet Browser VCS Extension - Comprehensive Test Plan

## 📋 Test Overview

**Project**: Comet Browser VCS Extension
**Version**: 1.0.0
**Test Environment**: Chrome Browser + Hybrid VCS Backend
**Test Duration**: ~45 minutes for full test suite

---

## 🎯 Pre-Test Setup

### 1. Backend Server Configuration
- ✅ **Status**: Server running on `http://localhost:8081`
- ✅ **Health Check**: `GET /health` returns `{"status": "healthy", "connected": true}`
- ✅ **VCS Repository**: Initialized and ready

### 2. Extension Installation
- ✅ **Chrome Extensions**: Navigate to `chrome://extensions/`
- ✅ **Developer Mode**: Enable "Developer mode" toggle
- ✅ **Load Extension**: Click "Load unpacked" → Select `comet-browser-extension` folder
- ✅ **Verification**: ☄️ Comet VCS icon appears in toolbar

---

## 🧪 TEST SUITE EXECUTION

## **PHASE 1: Basic Functionality Tests**

### **Test 1.1: Extension Loading & UI**
**Objective**: Verify extension loads and displays correctly

**Steps**:
1. Click ☄️ Comet VCS icon in Chrome toolbar
2. Verify popup appears with gradient background
3. Check all buttons are visible and clickable:
   - 💾 Save Current Page
   - 📝 Save Selection
   - 📚 View History
   - ⚙️ Settings

**Expected Results**:
- ✅ Popup displays with modern UI
- ✅ All buttons functional and responsive
- ✅ No console errors in DevTools

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

### **Test 1.2: Backend Connectivity**
**Objective**: Verify extension can communicate with VCS server

**Steps**:
1. Open extension popup
2. Wait for status to appear
3. Check status indicator shows "Connected" (green)

**Expected Results**:
- ✅ Status shows "Connected" or "Hybrid VCS is ready"
- ✅ No connection errors in console
- ✅ Server responds to health checks

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

## **PHASE 2: Content Saving Tests**

### **Test 2.1: Save Current Webpage**
**Objective**: Test complete webpage versioning

**Test URLs**:
- `https://example.com`
- `https://httpbin.org/html`
- `https://github.com/microsoft/vscode`

**Steps**:
1. Navigate to test URL
2. Click ☄️ Comet VCS icon
3. Click "💾 Save Current Page"
4. Wait for success notification
5. Check Chrome notification appears

**Expected Results**:
- ✅ Success notification: "Page Saved"
- ✅ Status shows: "Page saved with commit: [hash]"
- ✅ No errors in popup or console
- ✅ Progress indicator works (if visible)

**Test Results**:
| URL | Save Time | Status | Commit Hash |
|-----|-----------|--------|-------------|
| example.com | | [ ] Pass / [ ] Fail | |
| httpbin.org | | [ ] Pass / [ ] Fail | |
| github.com | | [ ] Pass / [ ] Fail | |

---

### **Test 2.2: Save Text Selection**
**Objective**: Test text selection versioning

**Steps**:
1. Navigate to `https://en.wikipedia.org/wiki/Web_browser`
2. Select paragraph of text (50-100 words)
3. Click ☄️ Comet VCS icon
4. Click "📝 Save Selection"
5. Verify selection highlighting (brief flash)

**Expected Results**:
- ✅ Selected text briefly highlights
- ✅ Success notification: "Selection Saved"
- ✅ Status shows selection details
- ✅ Context and metadata preserved

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

### **Test 2.3: Save Multiple Selections**
**Objective**: Test consecutive selection saves

**Steps**:
1. Make 3 different text selections on same page
2. Save each selection
3. Verify each save works independently

**Expected Results**:
- ✅ Each selection saves successfully
- ✅ Different commit hashes generated
- ✅ No interference between saves

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

### **Test 2.4: Save Link via Context Menu**
**Objective**: Test right-click link saving

**Steps**:
1. Find a hyperlink on any webpage
2. Right-click the link
3. Select "Save Link to VCS"
4. Verify notification appears

**Expected Results**:
- ✅ Context menu option appears
- ✅ Link saves successfully
- ✅ Notification confirms save

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

## **PHASE 3: History & Search Tests**

### **Test 3.1: History Viewer Access**
**Objective**: Test history interface opening

**Steps**:
1. Click ☄️ Comet VCS icon
2. Click "📚 View History"
3. Verify new tab opens with history interface

**Expected Results**:
- ✅ New tab opens: `chrome-extension://[id]/history.html`
- ✅ History UI loads with search/filter controls
- ✅ No loading errors

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

### **Test 3.2: History Content Display**
**Objective**: Verify saved content appears in history

**Steps**:
1. Open History viewer
2. Verify all saved items appear
3. Check item details (title, type, timestamp, commit hash)
4. Click on an item to view details

**Expected Results**:
- ✅ All saved pages/selections/links appear
- ✅ Item details display correctly
- ✅ Modal popup shows full content
- ✅ Timestamps and commit hashes visible

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

### **Test 3.3: History Search & Filtering**
**Objective**: Test search and filter functionality

**Steps**:
1. Use search box: "example"
2. Test filters: All, Webpages, Selections, Links
3. Combine search + filters
4. Verify results update dynamically

**Expected Results**:
- ✅ Search filters results in real-time
- ✅ Type filters work correctly
- ✅ Combined search + filter works
- ✅ No results show empty state message

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

## **PHASE 4: Keyboard Shortcuts Tests**

### **Test 4.1: Page Save Shortcut**
**Objective**: Test Ctrl+Shift+S keyboard shortcut

**Steps**:
1. Navigate to any webpage
2. Press `Ctrl+Shift+S` (or `Cmd+Shift+S` on Mac)
3. Verify page saves without opening popup

**Expected Results**:
- ✅ Page saves immediately
- ✅ Notification appears
- ✅ No popup interaction required

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

### **Test 4.2: Selection Save Shortcut**
**Objective**: Test Ctrl+Shift+V keyboard shortcut

**Steps**:
1. Select text on webpage
2. Press `Ctrl+Shift+V` (or `Cmd+Shift+V` on Mac)
3. Verify selection saves

**Expected Results**:
- ✅ Selected text saves
- ✅ Highlight effect appears
- ✅ Notification confirms save

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

## **PHASE 5: Error Handling Tests**

### **Test 5.1: Server Unavailable**
**Objective**: Test behavior when server is down

**Steps**:
1. Stop the VCS server (`Ctrl+C` in terminal)
2. Try to save a webpage
3. Check error handling

**Expected Results**:
- ✅ Error status appears in popup
- ✅ Clear error message displayed
- ✅ Graceful degradation

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

### **Test 5.2: Invalid Content Handling**
**Objective**: Test edge cases and invalid inputs

**Steps**:
1. Try to save empty selection
2. Attempt to save on chrome:// URLs
3. Test with very long page titles

**Expected Results**:
- ✅ Appropriate error messages
- ✅ No crashes or hangs
- ✅ Graceful error recovery

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

## **PHASE 6: Performance Tests**

### **Test 6.1: Large Page Save**
**Objective**: Test performance with large content

**Steps**:
1. Find a large webpage (news article, documentation)
2. Save the page
3. Measure save time and memory usage

**Expected Results**:
- ✅ Save completes within 10 seconds
- ✅ No memory leaks
- ✅ Progress indication works

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

### **Test 6.2: Rapid Saves**
**Objective**: Test handling multiple rapid saves

**Steps**:
1. Save 5 pages quickly in succession
2. Check all saves complete successfully
3. Verify history shows all items

**Expected Results**:
- ✅ All saves complete
- ✅ No queuing issues
- ✅ History shows all items correctly

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

## **PHASE 7: UI/UX Tests**

### **Test 7.1: Visual Indicators**
**Objective**: Test VCS active indicators

**Steps**:
1. Visit any webpage
2. Wait for indicator to appear (top-right corner)
3. Click indicator (should open extension)

**Expected Results**:
- ✅ Subtle indicator appears after 3 seconds
- ✅ Indicator clickable and functional
- ✅ Auto-hides after interaction

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

### **Test 7.2: Responsive Design**
**Objective**: Test popup on different screen sizes

**Steps**:
1. Resize browser window
2. Test popup positioning
3. Verify text and buttons remain readable

**Expected Results**:
- ✅ Popup stays within viewport
- ✅ All elements accessible
- ✅ No layout breaks

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

## **PHASE 8: Integration Tests**

### **Test 8.1: Backend Data Verification**
**Objective**: Verify data persistence in VCS

**Steps**:
1. Save several items via extension
2. Check backend database directly
3. Verify Git commits created
4. Check file structure in repository

**Expected Results**:
- ✅ Database contains saved items
- ✅ Git commits created for each save
- ✅ Proper file structure maintained

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

### **Test 8.2: Cross-Session Persistence**
**Objective**: Test data persistence across browser sessions

**Steps**:
1. Save content in current session
2. Close and reopen browser
3. Check history still contains saved items
4. Verify server restart doesn't lose data

**Expected Results**:
- ✅ All data persists across sessions
- ✅ History loads correctly after restart
- ✅ No data corruption

**Status**: [ ] Pass / [ ] Fail
**Notes**:

---

## 📊 TEST EXECUTION SUMMARY

### **Overall Test Status**
- **Total Tests**: 18 individual tests
- **Estimated Time**: 45-60 minutes
- **Prerequisites**: Chrome browser, Hybrid VCS server on port 8081

### **Test Coverage Areas**
- ✅ Extension Installation & Loading
- ✅ Backend Communication
- ✅ Content Saving (Pages, Selections, Links)
- ✅ History Management
- ✅ Keyboard Shortcuts
- ✅ Error Handling
- ✅ Performance
- ✅ UI/UX
- ✅ Data Persistence

### **Success Criteria**
- **Minimum Pass Rate**: 80% of tests pass
- **Critical Tests**: Must pass 100% (connectivity, basic saving)
- **Performance**: All operations complete within 10 seconds
- **Stability**: No crashes or data corruption

### **Post-Test Actions**
1. **Report Generation**: Document all test results
2. **Bug Tracking**: Log any failed tests with details
3. **Performance Metrics**: Record timing and resource usage
4. **User Feedback**: Gather usability observations

---

## 🚀 QUICK START TEST (5 minutes)

For immediate validation, run these critical tests:

1. **Extension Loads**: Click icon → Popup appears
2. **Connectivity**: Status shows "Connected"
3. **Basic Save**: Save any webpage → Success notification
4. **History**: View history → Saved item appears
5. **Shortcut**: `Ctrl+Shift+S` → Page saves

**If all 5 pass → Core functionality is working!** 🎉

---

## 🐛 Bug Report Template

**Test Case**: [Test ID]
**Steps to Reproduce**:
1.
2.
3.

**Expected Result**:
**Actual Result**:
**Browser Version**:
**OS Version**:
**Error Messages**:
**Screenshots**:

---

**Test Plan Version**: 1.0 | **Last Updated**: January 2026 | **Author**: Comet VCS Team
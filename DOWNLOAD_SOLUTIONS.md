# ComfyWorkflows.com Download Solutions

This document describes multiple solutions for downloading workflows from ComfyWorkflows.com.

## Solution Overview

| Solution | Status | Best For | Difficulty |
|---------|--------|----------|------------|
| **Playwright Script** | ✅ Working | Automation, CLI users | Medium |
| **Chrome Extension** | ✅ Ready | Browser users, one-click | Easy |
| **Manual Download** | ✅ Always works | Everyone | Easy |
| **Original Script** | ⚠️ Limited | Simple cases | Easy |

## 1. Playwright Script (Recommended for Automation)

### Installation

```bash
pip install playwright
playwright install chromium
```

### Usage

```bash
python download_workflow_playwright.py https://comfyworkflows.com/workflows/[id]
```

### How It Works

- Uses Playwright to render JavaScript
- Intercepts network requests to find workflow API calls
- Extracts workflow JSON from API responses
- Saves workflow to `workflows/downloaded/comfyworkflows/`

### Features

- ✅ Handles JavaScript-rendered pages
- ✅ Intercepts API calls automatically
- ✅ Tries multiple extraction strategies
- ✅ Works headless (no browser window)

### Limitations

- Requires Playwright installation (~100MB)
- May not work for private/authenticated workflows
- Some workflows may use non-standard data structures

## 2. Chrome Extension (Recommended for Browser Users)

### Installation

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `chrome_extension/` folder

### Usage

1. Navigate to any workflow page on ComfyWorkflows.com
2. Click the green "📥 Download Workflow" button (appears on the page)
3. Or use the extension popup

### Features

- ✅ One-click download
- ✅ Works automatically on workflow pages
- ✅ No command line needed
- ✅ Visual feedback

### File Location

Workflows are saved to your default Chrome download folder.

## 3. Manual Download (Always Works)

### Steps

1. Open the workflow page in your browser
2. Press **F12** to open Developer Tools
3. Go to the **Network** tab
4. Reload the page (F5)
5. Look for API calls (filter by "XHR" or "Fetch")
6. Find the response that contains `"nodes"` in the JSON
7. Right-click the response → **Copy** → **Copy response**
8. Save as `.json` file
9. Drag and drop into ComfyUI

### Alternative: Use Download Button

Many workflow pages have a "Download" button that directly downloads the JSON file.

## 4. Original Script (Basic)

### Usage

```bash
python download_workflow.py https://comfyworkflows.com/workflows/[id]
```

### Status

- ✅ Correctly identifies workflow URLs
- ⚠️ Cannot extract workflow data (JavaScript rendering)
- ✅ Provides helpful instructions

## Comparison

### Playwright vs Chrome Extension

| Feature | Playwright | Chrome Extension |
|---------|-----------|------------------|
| Setup | Install Python package | Load extension |
| Usage | Command line | Browser button |
| Automation | ✅ Yes | ⚠️ Manual click |
| Headless | ✅ Yes | ❌ No |
| User-friendly | ⚠️ Technical | ✅ Very easy |

### When to Use What

- **Playwright**: If you want to automate downloads, use scripts, or download many workflows
- **Chrome Extension**: If you browse workflows in Chrome and want one-click downloads
- **Manual**: If other methods fail or you want full control

## Troubleshooting

### Playwright: "Could not extract workflow data"

- The workflow may be private or require authentication
- Try manual download method
- Check if the workflow page loads correctly in a regular browser

### Chrome Extension: Button doesn't appear

- Make sure you're on a workflow page (URL contains `/workflow/` or `/workflows/`)
- Refresh the page after installing the extension
- Check that the extension is enabled in `chrome://extensions/`

### Manual: Can't find workflow JSON

- Make sure you're looking in the Network tab
- Filter by "XHR" or "Fetch" to see API calls
- Look for responses with `application/json` content type
- The workflow JSON should contain a `"nodes"` key

## Testing

Test with this workflow:
```
https://comfyworkflows.com/workflows/3e83739d-cb2d-43c3-b137-24ca7146b628
```

## Future Improvements

- [ ] Add authentication support for private workflows
- [ ] Batch download multiple workflows
- [ ] Integration with ComfyUI Manager
- [ ] Workflow validation after download
- [ ] Auto-install missing custom nodes

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the script/extension code
3. Try the manual download method as a fallback

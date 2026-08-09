# ComfyWorkflows Downloader - Chrome Extension

A Chrome extension to easily download ComfyUI workflows from ComfyWorkflows.com with one click.

## Features

- 🚀 One-click workflow download
- 📥 Automatic workflow extraction from JavaScript-rendered pages
- 🎯 Works on all ComfyWorkflows.com workflow pages
- 💾 Downloads workflow JSON files ready to use in ComfyUI

## Installation

### Option 1: Load Unpacked Extension (Development)

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome_extension` folder
5. The extension is now installed!

### Option 2: Package Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Pack extension"
4. Select the `chrome_extension` folder
5. Install the generated `.crx` file

## Usage

### Method 1: Download Button on Page

1. Navigate to any workflow page on ComfyWorkflows.com:
   - `https://comfyworkflows.com/workflow/[id]`
   - `https://comfyworkflows.com/workflows/[id]`
2. Look for the green "📥 Download Workflow" button in the top-right corner
3. Click it to download the workflow JSON file

### Method 2: Extension Popup

1. Navigate to a workflow page
2. Click the extension icon in Chrome's toolbar
3. Click "Download Current Workflow"

## How It Works

The extension:
1. Monitors workflow pages for workflow data
2. Extracts workflow JSON from:
   - Window objects (React/Next.js state)
   - Network API responses
   - Page JavaScript context
3. Downloads the workflow as a JSON file
4. Saves it to your default download folder

## File Structure

```
chrome_extension/
├── manifest.json       # Extension configuration
├── content.js          # Script that runs on workflow pages
├── background.js       # Background service worker
├── popup.html          # Extension popup UI
├── popup.js            # Popup functionality
├── icons/              # Extension icons (create these)
└── README.md           # This file
```

## Creating Icons

You'll need to create icon files:
- `icons/icon16.png` (16x16 pixels)
- `icons/icon48.png` (48x48 pixels)
- `icons/icon128.png` (128x128 pixels)

You can use any image editor or online icon generator.

## Troubleshooting

### Extension doesn't work

1. Make sure you're on a workflow page (not a listing page)
2. Refresh the page after installing the extension
3. Check Chrome's extension error page: `chrome://extensions/`
4. Open DevTools (F12) and check the Console for errors

### Workflow not found

- The page may need more time to load
- Try refreshing the page
- Use the browser's Network tab to manually find the workflow JSON

### Download button not appearing

- Make sure the extension is enabled
- Check that you're on a workflow page (URL contains `/workflow/` or `/workflows/`)
- Refresh the page

## Development

To modify the extension:

1. Make changes to the files
2. Go to `chrome://extensions/`
3. Click the refresh icon on the extension card
4. Test your changes

## Permissions

The extension requires:
- `activeTab`: To access the current tab's content
- `downloads`: To download workflow files
- `storage`: To store settings (future use)
- `https://comfyworkflows.com/*`: To access ComfyWorkflows.com

## License

This extension is provided as-is for downloading ComfyUI workflows.

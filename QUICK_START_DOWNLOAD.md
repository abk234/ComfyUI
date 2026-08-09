# Quick Start: Download Workflows from ComfyWorkflows.com

## 🚀 Fastest Method: Chrome Extension

1. **Install Extension:**
   ```bash
   # Open Chrome → chrome://extensions/
   # Enable "Developer mode" → "Load unpacked"
   # Select: chrome_extension/ folder
   ```

2. **Use It:**
   - Go to any workflow page on ComfyWorkflows.com
   - Click the green "📥 Download Workflow" button
   - Done! ✅

## 🤖 Automated Method: Playwright Script

1. **Install:**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Use:**
   ```bash
   python download_workflow_playwright.py https://comfyworkflows.com/workflows/[id]
   ```

## 📋 Manual Method (Always Works)

1. Open workflow page in browser
2. Press **F12** → **Network** tab
3. Reload page
4. Find API call with JSON containing `"nodes"`
5. Copy JSON → Save as `.json` file
6. Drag into ComfyUI

## 📁 Where Workflows Are Saved

- **Playwright script: `workflows/downloaded/comfyworkflows/`**
- **Chrome Extension: Your default download folder**
- **Manual: Wherever you save it**

## 🎯 Test It

Try with this workflow:
```bash
python download_workflow_playwright.py https://comfyworkflows.com/workflows/3e83739d-cb2d-43c3-b137-24ca7146b628
```

## 📚 More Info

See `DOWNLOAD_SOLUTIONS.md` for detailed documentation.

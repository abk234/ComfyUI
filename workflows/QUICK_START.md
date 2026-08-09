# Quick Start Guide

## Install Dependencies

The download scripts require the `requests` library:

```bash
pip install requests pillow
```

## Search for V07 Workflows

```bash
# Interactive search
python workflows/search_workflows.py "V07"

# Direct search
python download_workflow.py --search "V07"
```

## Search for Qwen3-TTS Workflows

```bash
python workflows/search_workflows.py "qwen3tts" --type qwen3tts
```

## Search for Z-Image Workflows

```bash
python workflows/search_workflows.py "z-image" --type zimage
```

## Download from URL

```bash
python download_workflow.py https://civitai.com/models/12345
```

## Validate Workflows

Before using a workflow, validate dependencies:

```bash
python validate_workflow.py <workflow.json>
```

This ensures all models, custom nodes, and dependencies are available.

## Load Workflows in ComfyUI

1. **Validate first**: `python validate_workflow.py workflow.json`
2. **Install missing dependencies** via ComfyUI Manager UI
3. **Open ComfyUI**
4. **Drag and drop** the `.json` file into the browser window
5. **Or use** File → Load → select workflow file

## Directory Structure

```
workflows/
├── downloaded/     # All downloaded workflows (organized by model)
├── qwen3tts/       # Qwen3-TTS workflows
└── zimage/         # Z-Image workflows
```

## Need Help?

- See `WORKFLOW_GUIDE.md` for detailed instructions
- Check `README.md` in each workflow directory
- Review ComfyUI console for error messages

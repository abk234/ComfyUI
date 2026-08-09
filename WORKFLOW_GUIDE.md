# ComfyUI Workflow Management Guide

This guide explains how to search, download, and use workflows in ComfyUI, with special focus on Qwen3-TTS and Z-Image workflows.

## Quick Start

### Search and Download Workflows

1. **Search for workflows on CivitAI:**
   ```bash
   python download_workflow.py --search "V07"
   ```

2. **Download from a specific URL:**
   ```bash
   python download_workflow.py https://civitai.com/models/12345
   ```

3. **Interactive search (recommended):**
   ```bash
   python workflows/search_workflows.py
   ```

### Using Downloaded Workflows

1. **In ComfyUI UI:**
   - Drag and drop the `.json` file into the ComfyUI browser window
   - Or use File → Load → select the workflow file

2. **Via API:**
   - Load the JSON file and POST it to `/prompt` endpoint

## Finding Qwen3-TTS Workflows

Qwen3-TTS (Text-to-Speech) workflows allow you to generate high-quality speech from text.

### Search Commands

```bash
# Search for Qwen3-TTS workflows
python workflows/search_workflows.py "qwen3tts" --type qwen3tts

# Or use the download script
python download_workflow.py --search "qwen3tts"
```

### Setup Requirements

1. **Install Custom Node:**
   - Use ComfyUI Manager to install "ComfyUI-Qwen-TTS"
   - Or clone: `git clone https://github.com/flybirdxx/ComfyUI-Qwen-TTS.git custom_nodes/ComfyUI-Qwen-TTS`

2. **Download Model:**
   - Model: `Qwen3-TTS-12Hz-1.7B-Base`
   - From: https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base

3. **Place Models:**
   - Follow the custom node's instructions for model placement

## Finding Z-Image Workflows

Z-Image workflows provide fast, high-quality image generation.

### Search Commands

```bash
# Search for Z-Image workflows
python workflows/search_workflows.py "z-image" --type zimage

# Or use the download script
python download_workflow.py --search "z-image"
```

### Setup Requirements

1. **Download Three Model Files:**
   - `zImage_turbo.safetensors` → `models/checkpoints/`
   - `zImage_vae.safetensors` → `models/vae/`
   - `zImage_textEncoder.safetensors` → `models/clip/`

2. **Verify Installation:**
   - Models should appear in ComfyUI's model dropdowns
   - Test with a simple Z-Image workflow

## Workflow Organization

Downloaded workflows are organized in:

```
workflows/
├── downloaded/          # Workflows from CivitAI
│   └── [model-name]/   # Organized by model
├── qwen3tts/           # Qwen3-TTS specific workflows
└── zimage/             # Z-Image specific workflows
```

## Examples

### Example 1: Search for V07 Workflows

```bash
python workflows/search_workflows.py "V07"
```

This will:
1. Search CivitAI for models matching "V07"
2. Show you a list of potential workflows
3. Let you select which ones to download

### Example 2: Download Specific Workflow

```bash
python download_workflow.py https://civitai.com/models/2174530
```

This downloads all workflow files from that model page.

### Example 3: Batch Download Qwen3-TTS Workflows

```bash
python workflows/search_workflows.py "qwen3tts" --type qwen3tts
# Then select 'a' to download all results
```

## Validating Workflows

Before using a workflow, validate that all dependencies are met:

```bash
python validate_workflow.py <workflow.json>
```

This checks for:
- ✅ Missing models (checkpoints, VAE, LoRA, etc.)
- ✅ Missing custom nodes
- ✅ Missing Python dependencies
- ✅ Integration with ComfyUI Manager

### Quick Validation Example

```bash
# Validate a downloaded workflow
python validate_workflow.py workflows/downloaded/some-model/workflow.json

# Generate fix script
python validate_workflow.py workflows/downloaded/some-model/workflow.json --fix
```

See `WORKFLOW_VALIDATION_GUIDE.md` for detailed information.

## Troubleshooting

### Script Errors

**"ModuleNotFoundError: No module named 'requests'"**
```bash
pip install requests pillow
```

**"No workflow files found"**
- The model page might not have workflow files
- Try a different model or search term
- Some workflows are embedded in PNG images

### Workflow Loading Issues

**Missing Custom Nodes:**
- Check the workflow JSON for node class names
- Install missing custom nodes via ComfyUI Manager
- Restart ComfyUI after installation
- Use `validate_workflow.py` to identify missing nodes

**Missing Models:**
- Use `validate_workflow.py` to identify missing models
- Check if models are available in ComfyUI Manager
- Install via Manager UI (filter by "In Workflow")
- Or download manually and place in correct directories

**Workflow Errors:**
- Validate workflow first: `python validate_workflow.py workflow.json`
- Verify all dependencies are installed
- Check ComfyUI console for specific errors
- Ensure model paths are correct

## Advanced Usage

### Custom Workflow Directory

```bash
python download_workflow.py --workflows-dir /path/to/workflows https://civitai.com/models/12345
```

### Programmatic Access

You can also use the download functions in your own scripts:

```python
from download_workflow import download_workflow_from_url, search_civitai_models

# Search
results = search_civitai_models("V07", limit=10)

# Download
download_workflow_from_url("https://civitai.com/models/12345")
```

## Resources

- **CivitAI**: https://civitai.com/models?search=comfyui
- **Qwen3-TTS**: https://github.com/flybirdxx/ComfyUI-Qwen-TTS
- **Z-Image**: Search for "z-image" on HuggingFace or CivitAI
- **ComfyUI Docs**: https://docs.comfy.org/

## Tips

1. **Use specific search terms**: "V07", "qwen3tts", "z-image" work better than generic terms
2. **Check model pages**: Even if a model isn't a workflow, it might have workflow files in its versions
3. **PNG workflows**: Some workflows are embedded in PNG images - the script extracts them automatically
4. **Organize downloads**: Workflows are automatically organized by model name
5. **Version control**: Different versions of the same model may have different workflows

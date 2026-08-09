# Workflow Validation Guide

This guide explains how to ensure workflows from ComfyUI Manager or the community have all their dependencies met.

## Quick Start

### Validate a Workflow

```bash
python validate_workflow.py <workflow.json>
```

This will check for:
- ✅ Missing models (checkpoints, VAE, LoRA, etc.)
- ✅ Missing custom nodes
- ✅ Missing Python dependencies
- ✅ Integration with ComfyUI Manager

### Example

```bash
python validate_workflow.py workflows/downloaded/some-model/workflow.json
```

## Understanding the Validation Report

### ✅ All Models Available
If all models are found, you'll see:
```
✅ All models are available!
✅ All custom nodes are available!
✅ WORKFLOW IS READY TO USE!
```

### ❌ Missing Models

If models are missing, you'll see:
```
❌ MISSING MODELS:
  CHECKPOINTS:
    • model_name.safetensors
      ✓ Available in Model Manager
      → Download URL: https://...
      → Action: Install via ComfyUI Manager UI
```

### Model Manager Integration

The validator checks if missing models are in ComfyUI Manager's model list:

- **✓ Available in Model Manager**: Model has a download URL and can be installed via UI
- **⚠ In Model Manager but needs URL**: Model is listed but URL needs to be updated
- **✗ Not in Model Manager**: Model needs to be added to model-list.json or downloaded manually

## Installing Missing Dependencies

### Method 1: Via ComfyUI Manager UI (Recommended)

1. **Open ComfyUI** in your browser
2. **Go to Manager** → **Model Manager**
3. **Filter by "In Workflow"** to see only models used in your workflow
4. **Click "Install"** on missing models
5. Models will download automatically to the correct location

### Method 2: Using the Fix Script

Generate a fix script:
```bash
python validate_workflow.py <workflow.json --fix
```

This creates a `.fix.sh` script that you can review and run:
```bash
bash workflow.json.fix.sh
```

### Method 3: Manual Download

1. Check the validation report for download URLs
2. Download models manually
3. Place them in the correct directories:
   - Checkpoints: `models/checkpoints/`
   - VAE: `models/vae/`
   - LoRA: `models/loras/`
   - ControlNet: `models/controlnet/`

## Installing Custom Nodes

### Via ComfyUI Manager UI

1. **Go to Manager** → **Install Custom Nodes**
2. **Search** for the node name (e.g., "Qwen3-TTS", "Z-Image")
3. **Click "Install"**
4. **Restart ComfyUI**

### Manual Installation

```bash
cd custom_nodes
git clone <repository-url>
cd <node-name>
pip install -r requirements.txt  # If requirements.txt exists
```

## Workflow Types

### Qwen3-TTS Workflows

**Required:**
1. Custom Node: `ComfyUI-Qwen-TTS`
2. Model: `Qwen3-TTS-12Hz-1.7B-Base`

**Validation:**
```bash
python validate_workflow.py workflows/qwen3tts/example.json
```

**Install:**
- Custom node: Install via Manager or `git clone https://github.com/flybirdxx/ComfyUI-Qwen-TTS.git`
- Model: Download from HuggingFace

### Z-Image Workflows

**Required:**
1. Three model files:
   - `zImage_turbo.safetensors` → `models/checkpoints/`
   - `zImage_vae.safetensors` → `models/vae/`
   - `zImage_textEncoder.safetensors` → `models/clip/`

**Validation:**
```bash
python validate_workflow.py workflows/zimage/example.json
```

## Integration with ComfyUI Manager

ComfyUI Manager maintains a `model-list.json` file that maps model filenames to download URLs. The validator:

1. **Checks** if missing models are in the list
2. **Shows** download URLs if available
3. **Indicates** if models need to be added to the list

### Adding Models to Model Manager

If a model is missing from Manager:

1. **Find the model** on HuggingFace, CivitAI, or other sources
2. **Get the download URL**
3. **Edit** `custom_nodes/ComfyUI-Manager/model-list.json`
4. **Add entry:**
   ```json
   {
     "filename": "model_name.safetensors",
     "name": "Model Display Name",
     "url": "https://download-url-here",
     "size": "1.5GB",
     "type": "checkpoint"
   }
   ```
5. **Update cache:**
   ```bash
   python update-model-cache-simple.py
   ```
6. **Restart ComfyUI**

## Troubleshooting

### Models Not Detected

If models exist but aren't detected:

1. **Clear cache:**
   ```bash
   python clear-model-cache.py
   ```

2. **Check file permissions**

3. **Verify file extensions** match expected types

### Custom Nodes Not Found

1. **Check installation:**
   ```bash
   ls custom_nodes/
   ```

2. **Verify node class name** matches the workflow

3. **Check for typos** in node class names

### Python Dependencies Missing

1. **Check requirements.txt** in custom node directory
2. **Install manually:**
   ```bash
   pip install <package-name>
   ```

### Model Manager Not Working

1. **Verify ComfyUI Manager is installed:**
   ```bash
   ls custom_nodes/ComfyUI-Manager/
   ```

2. **Update model cache:**
   ```bash
   python update-model-cache-simple.py
   ```

3. **Check model-list.json** exists and is valid JSON

## Best Practices

1. **Validate before use**: Always validate workflows before loading them
2. **Check Manager first**: Use ComfyUI Manager UI for easy installation
3. **Keep Manager updated**: Regularly update model-list.json
4. **Document workflows**: Note required models and nodes
5. **Use fix scripts**: Review and use generated fix scripts

## Example Workflow

```bash
# 1. Download workflow
python download_workflow.py --search "V07"

# 2. Validate workflow
python validate_workflow.py workflows/downloaded/v07-model/workflow.json

# 3. Install missing dependencies via Manager UI or fix script
python validate_workflow.py workflows/downloaded/v07-model/workflow.json --fix

# 4. Re-validate to confirm
python validate_workflow.py workflows/downloaded/v07-model/workflow.json
```

## Related Scripts

- `download_workflow.py` - Download workflows from CivitAI
- `validate_workflow.py` - Validate workflow dependencies (this script)
- `check-missing-models.py` - Simple model checker
- `fix-workflow-models.py` - Fix workflow by replacing models
- `update-model-cache-simple.py` - Update Model Manager cache

## See Also

- `WORKFLOW_GUIDE.md` - General workflow guide
- `workflows/README.md` - Workflows directory documentation
- `MODEL_MANAGER_UPDATE.md` - Model Manager update guide

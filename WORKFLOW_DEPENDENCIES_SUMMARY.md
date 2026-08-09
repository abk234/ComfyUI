# Workflow Dependencies Management Summary

This document explains how to ensure workflows from ComfyUI Manager or the community have all their dependencies met.

## Overview

ComfyUI Manager provides workflow templates from custom nodes and the community. To use these workflows, you need to ensure:

1. ✅ **Models are installed** (checkpoints, VAE, LoRA, etc.)
2. ✅ **Custom nodes are installed**
3. ✅ **Python dependencies are met**

## Quick Workflow

### Step 1: Get Workflow

**From ComfyUI Manager:**
- Open ComfyUI → Manager → Workflow Templates
- Browse templates from installed custom nodes
- Click to load a template

**From Community (CivitAI, etc.):**
```bash
python download_workflow.py --search "V07"
python workflows/search_workflows.py "qwen3tts" --type qwen3tts
```

### Step 2: Validate Workflow

```bash
python validate_workflow.py <workflow.json>
```

This will show:
- ✅ What's available
- ❌ What's missing
- 📋 How to install missing items

### Step 3: Install Dependencies

**Via ComfyUI Manager UI (Easiest):**
1. Open ComfyUI → Manager → Model Manager
2. Filter by "In Workflow"
3. Click "Install" on missing models
4. Go to Manager → Install Custom Nodes
5. Search and install missing nodes

**Via Fix Script:**
```bash
python validate_workflow.py <workflow.json> --fix
bash <workflow.json>.fix.sh  # Review first!
```

**Manually:**
- Download models and place in correct directories
- Install custom nodes via git clone
- Install Python packages via pip

### Step 4: Re-validate

```bash
python validate_workflow.py <workflow.json>
```

Should show: ✅ WORKFLOW IS READY TO USE!

## ComfyUI Manager Integration

### How Manager Helps

1. **Model Manager:**
   - Maintains `model-list.json` with download URLs
   - Shows models used in workflows
   - Provides one-click installation
   - Filters by "In Workflow" to see only needed models

2. **Custom Node Manager:**
   - Lists available custom nodes
   - Shows which nodes are installed
   - Provides installation via UI

3. **Workflow Templates:**
   - Custom nodes can include example workflows
   - Accessible via Manager → Workflow Templates
   - Automatically served from `example_workflows/` folders

### Model Manager Workflow Detection

When you load a workflow in ComfyUI:
1. ComfyUI validates the workflow
2. Missing models create validation errors
3. ComfyUI Manager checks `model-list.json`
4. If found, models appear in Model Manager UI
5. You can click "Install" to download them

### Adding Models to Manager

If a model isn't in Manager's list:

1. **Find the model** (HuggingFace, CivitAI, etc.)
2. **Get download URL**
3. **Edit** `custom_nodes/ComfyUI-Manager/model-list.json`:
   ```json
   {
     "filename": "model.safetensors",
     "name": "Model Name",
     "url": "https://download-url",
     "size": "1.5GB",
     "type": "checkpoint"
   }
   ```
4. **Update cache:**
   ```bash
   python update-model-cache-simple.py
   ```
5. **Restart ComfyUI**

## Validation Tool Features

The `validate_workflow.py` script provides:

### Checks Performed

1. **Model Availability:**
   - Checks all model types (checkpoints, VAE, LoRA, etc.)
   - Compares against installed models
   - Identifies missing models

2. **Model Manager Integration:**
   - Checks if missing models are in `model-list.json`
   - Shows download URLs if available
   - Indicates if URLs need updating

3. **Custom Node Detection:**
   - Identifies custom node classes used
   - Checks if custom nodes are installed
   - Lists missing custom nodes

4. **Dependency Checking:**
   - Checks for Python package requirements
   - Identifies missing packages

### Output Example

```
✅ All models are available!
❌ MISSING MODELS:
  CHECKPOINTS:
    • model.safetensors
      ✓ Available in Model Manager
      → Download URL: https://...
      → Action: Install via ComfyUI Manager UI

❌ MISSING CUSTOM NODES:
  • Qwen3TTSNode
    → Action: Install via ComfyUI Manager
```

## Workflow Types

### Qwen3-TTS Workflows

**Requirements:**
- Custom Node: `ComfyUI-Qwen-TTS`
- Model: `Qwen3-TTS-12Hz-1.7B-Base`

**Validation:**
```bash
python validate_workflow.py workflows/qwen3tts/example.json
```

**Installation:**
- Custom node: Manager → Install Custom Nodes → Search "Qwen-TTS"
- Model: Download from HuggingFace or add to Manager

### Z-Image Workflows

**Requirements:**
- `zImage_turbo.safetensors` → `models/checkpoints/`
- `zImage_vae.safetensors` → `models/vae/`
- `zImage_textEncoder.safetensors` → `models/clip/`

**Validation:**
```bash
python validate_workflow.py workflows/zimage/example.json
```

**Installation:**
- Download all three models
- Place in correct directories
- Or add to Model Manager for easier management

## Best Practices

1. **Always Validate First:**
   ```bash
   python validate_workflow.py workflow.json
   ```

2. **Use Manager UI When Possible:**
   - Easier than manual downloads
   - Automatic path management
   - Update tracking

3. **Keep Manager Updated:**
   - Regularly update `model-list.json`
   - Add community-requested models
   - Update download URLs if they change

4. **Document Workflows:**
   - Note required models and nodes
   - Include setup instructions
   - List any special requirements

5. **Test After Installation:**
   - Re-validate after installing dependencies
   - Test workflow execution
   - Verify outputs are correct

## Troubleshooting

### Models Not Showing in Manager

1. **Check model-list.json exists:**
   ```bash
   ls custom_nodes/ComfyUI-Manager/model-list.json
   ```

2. **Update cache:**
   ```bash
   python update-model-cache-simple.py
   ```

3. **Clear ComfyUI cache:**
   ```bash
   python clear-model-cache.py
   ```

4. **Restart ComfyUI**

### Validation Errors

1. **Check file paths** - ensure workflow file exists
2. **Verify JSON format** - workflow must be valid JSON
3. **Check ComfyUI installation** - ensure folder_paths works

### Models Installed But Not Detected

1. **Clear cache:**
   ```bash
   python clear-model-cache.py
   ```

2. **Check file extensions** - must match expected types
3. **Verify file permissions**
4. **Check extra_model_paths.yaml** - models might be in custom paths

## Related Tools

| Tool | Purpose |
|------|---------|
| `validate_workflow.py` | Comprehensive workflow validation |
| `download_workflow.py` | Download workflows from CivitAI |
| `check-missing-models.py` | Simple model availability check |
| `fix-workflow-models.py` | Replace missing models in workflow |
| `update-model-cache-simple.py` | Update Model Manager cache |
| `clear-model-cache.py` | Clear ComfyUI model cache |

## Example: Complete Workflow

```bash
# 1. Search and download workflow
python workflows/search_workflows.py "V07"

# 2. Validate workflow
python validate_workflow.py workflows/downloaded/v07-model/workflow.json

# 3. Install missing dependencies via Manager UI
#    - Open ComfyUI → Manager → Model Manager
#    - Filter by "In Workflow"
#    - Click "Install" on missing models

# 4. Re-validate
python validate_workflow.py workflows/downloaded/v07-model/workflow.json

# 5. Use workflow in ComfyUI
#    - Drag workflow.json into ComfyUI
#    - Should work without errors!
```

## See Also

- `WORKFLOW_VALIDATION_GUIDE.md` - Detailed validation guide
- `WORKFLOW_GUIDE.md` - General workflow usage
- `workflows/README.md` - Workflows directory info
- `MODEL_MANAGER_UPDATE.md` - Model Manager updates

## Summary

✅ **ComfyUI Manager** provides workflow templates and model management  
✅ **Validation tool** ensures all dependencies are met  
✅ **Model Manager** shows missing models with download links  
✅ **Fix scripts** automate dependency installation  
✅ **Always validate** before using workflows from the community

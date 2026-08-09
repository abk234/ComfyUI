# ✅ Model Manager Setup Complete

## What Was Done

I've successfully added the missing models to ComfyUI-Manager's model list so they will appear in the Model Manager UI when you open workflows.

### ✅ VAE Model - Complete
- **Model**: `vae-ft-mse-840000-ema-pruned.safetensors`
- **Status**: ✅ Added with working download URL
- **Download URL**: https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors
- **Size**: 335MB
- **Ready to download**: Yes

### ⚠️ V07 Checkpoint - Needs URL
- **Model**: `SD1.5/V07_v07.safetensors`
- **Status**: ⚠️ Added but needs download URL
- **Current URL**: Placeholder (needs update)
- **Note**: This model is used in comfyui-impact-pack example workflows but I couldn't find a public download URL

## How to Use

### 1. Restart ComfyUI
```bash
# Stop ComfyUI if running, then restart it
python3 main.py
```

### 2. Open a Workflow
When you open a workflow like `6-DetailerWildcard.json`:

1. **ComfyUI validates the workflow** and detects missing models
2. **Missing models appear in validation errors** (if any)
3. **Open Model Manager** (usually in the UI menu)
4. **Use the "In Workflow" filter** to see models used in your current workflow
5. **Missing models will appear** with download links (if URL is available)

### 3. Download Models

**For VAE Model:**
- ✅ Will appear with a working download link
- Click "Install" button or use the download icon
- Model will download to `models/vae/`

**For V07 Checkpoint:**
- ⚠️ Will appear in the list but download won't work until URL is updated
- To fix: Find the download URL and update it in `custom_nodes/ComfyUI-Manager/model-list.json`

## Finding the V07 Download URL

Since I couldn't find a public URL for V07_v07, you can:

1. **Check the workflow source** - Where did you get the workflow from?
2. **Search HuggingFace**:** https://huggingface.co/models?search=V07
3. **Search Civitai**: https://civitai.com/models?search=V07
4. **Check comfyui-impact-pack documentation** - It might mention where to get example models

Once you find the URL, update it in:
```
custom_nodes/ComfyUI-Manager/model-list.json
```

Find the V07 entry and change:
```json
"url": "PLACEHOLDER_UPDATE_WITH_ACTUAL_DOWNLOAD_URL"
```
to:
```json
"url": "https://your-actual-download-url-here"
```

Then run:
```bash
python3 update-model-cache-simple.py
```

## Testing

You can test the setup with:
```bash
python3 test-workflow-models.py
```

This will show you which models are missing and their status in Model Manager.

## Files Modified

- ✅ `custom_nodes/ComfyUI-Manager/model-list.json` - Added both models
- ✅ Cache updated at: `~/.cache/comfyui-manager/`

## Helper Scripts Created

- `check-missing-models.py` - Check which models are available
- `test-workflow-models.py` - Test workflow validation
- `update-model-cache-simple.py` - Update Model Manager cache
- `fix-workflow-models.py` - Auto-fix workflows to use available models

## Summary

✅ **VAE model is ready** - Will appear in Model Manager with working download link  
⚠️ **V07 checkpoint is listed** - Will appear but needs URL update to enable download

After restarting ComfyUI and opening a workflow, the missing models should automatically appear in the Model Manager UI!

# Model Manager Update - Missing Models Added

## ✅ What Was Done

I've added the missing models to ComfyUI-Manager's `model-list.json` so they will now appear in the Model Manager UI for download.

### 1. VAE Model - ✅ Complete
- **Model**: `vae-ft-mse-840000-ema-pruned.safetensors`
- **Status**: ✅ Added with download URL
- **URL**: https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors
- **Size**: 335MB
- **Location**: Will download to `models/vae/`

### 2. V07 Checkpoint - ⚠️ Needs URL Update
- **Model**: `V07_v07.safetensors`
- **Status**: ⚠️ Added but needs download URL
- **Current URL**: `PLACEHOLDER_UPDATE_WITH_ACTUAL_DOWNLOAD_URL`
- **Location**: Will download to `models/checkpoints/SD1.5/`

## 🔧 Next Steps

### For VAE Model:
1. **Restart ComfyUI** to refresh the Model Manager
2. Open the **Model Manager** in the UI
3. Search for "VAE FT MSE" or "vae-ft-mse"
4. Click **Download** - it will download automatically to the correct location

### For V07 Checkpoint:
You need to find the download URL for this model. Here's how:

1. **Search for the model** on:
   - HuggingFace: https://huggingface.co/models?search=V07
   - Civitai: https://civitai.com/models?search=V07
   - Or check where you originally got the workflow from

2. **Once you have the URL**, update it in:
   ```
   custom_nodes/ComfyUI-Manager/model-list.json
   ```
   
   Find the entry for "V07 v07" and update the `"url"` field from:
   ```json
   "url": "PLACEHOLDER_UPDATE_WITH_ACTUAL_DOWNLOAD_URL"
   ```
   to:
   ```json
   "url": "https://your-actual-download-url-here"
   ```

3. **After updating the URL**, run:
   ```bash
   python3 update-model-cache-simple.py
   ```

4. **Restart ComfyUI** and the model will appear in Model Manager

## 📝 Alternative: Manual Download

If you prefer to download manually:

### VAE Model:
```bash
cd models/vae
wget https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors
```

### V07 Checkpoint:
Download from your source and place at:
```
models/checkpoints/SD1.5/V07_v07.safetensors
```

## 🔍 Verification

After restarting ComfyUI, you can verify the models are available:

```bash
python3 check-missing-models.py
```

This will show you which models are now available.

## 📂 Files Modified

- `custom_nodes/ComfyUI-Manager/model-list.json` - Added both models
- Cache updated at: `~/.cache/comfyui-manager/`

## 🆘 Troubleshooting

If models don't appear in Model Manager after restart:

1. **Clear ComfyUI cache**:
   ```bash
   python3 clear-model-cache.py
   ```

2. **Update Model Manager cache**:
   ```bash
   python3 update-model-cache-simple.py
   ```

3. **Restart ComfyUI completely** (stop and start again)

4. **Check the browser console** for any errors when opening Model Manager

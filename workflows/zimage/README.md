# Z-Image Workflows

This directory contains workflows that use Z-Image, a fast and efficient image generation model.

## About Z-Image

Z-Image is a 6B parameter image generation model developed by Alibaba's Tongyi Lab using a Scalable Single-Stream DiT (S3-DiT) architecture. Z-Image-Turbo is a distilled version optimized for speed.

## Setup

### 1. Download Required Models

You need three model files:

1. **Diffusion Model**: `zImage_turbo.safetensors`
   - Place in: `models/checkpoints/`

2. **VAE**: `zImage_vae.safetensors`
   - Place in: `models/vae/`

3. **Text Encoder**: `zImage_textEncoder.safetensors`
   - Place in: `models/clip/`

### 2. Model Sources

Models can be downloaded from:
- HuggingFace: Search for "z-image" or "zimage"
- Official Z-Image repositories
- CivitAI: Search for "z-image" models

### 3. Verify Installation

After placing the models, verify they're detected by ComfyUI:
1. Start ComfyUI
2. Check that models appear in the model dropdowns
3. Load a Z-Image workflow to test

## Features

- **Speed**: Generates images in 13-30 seconds on 8GB VRAM
- **Quality**: Photorealistic visuals with sharp textures and faithful composition
- **Efficiency**: Optimized for low VRAM hardware (runs on 16GB VRAM)
- **Resolution**: Optimized up to 2K resolution
- **Fast Inference**: Sub-second latency on enterprise GPUs

## Using Workflows

1. Load a workflow JSON file from this directory into ComfyUI
2. Ensure all required models are loaded
3. Enter your text prompt
4. Adjust resolution and sampling settings (typically 8 steps for Turbo)
5. Generate image

## Workflow Structure

A typical Z-Image workflow includes:
- Model loader (UNET)
- CLIP text encoder (Qwen 3B)
- VAE autoencoder
- Text encoding (positive and negative prompts)
- Latent canvas creation with AuraFlow scheduler
- Sampling and decoding to RGB output

## Finding More Workflows

Search CivitAI for Z-Image workflows:
```bash
python ../search_workflows.py "z-image" --type zimage
```

Or use the download script:
```bash
python ../download_workflow.py --search "z-image"
```

## Performance Tips

- **Low VRAM**: Use the Turbo version and lower resolution
- **Speed**: Use 8-step sampling for fastest generation
- **Quality**: Increase steps to 20-30 for better quality (slower)
- **Resolution**: Start with 1024x1024, increase if VRAM allows

## Troubleshooting

### Models Not Loading
- Verify all three model files are in the correct directories
- Check file names match exactly (case-sensitive)
- Ensure models are complete downloads (check file sizes)

### Out of Memory Errors
- Use Z-Image-Turbo instead of full Z-Image
- Reduce resolution (try 768x768 or 512x512)
- Close other applications using GPU memory

### Generation Errors
- Verify AuraFlow scheduler is available
- Check that all nodes in the workflow are compatible
- Review ComfyUI console for specific error messages

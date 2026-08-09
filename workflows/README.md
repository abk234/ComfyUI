# ComfyUI Workflows

This directory contains downloaded and organized ComfyUI workflows, including specialized workflows for Qwen3-TTS and Z-Image.

## Directory Structure

- `downloaded/` - Workflows downloaded from CivitAI and other sources
- `qwen3tts/` - Workflows using Qwen3-TTS (Text-to-Speech)
- `zimage/` - Workflows using Z-Image (Fast Image Generation)

## Using Workflows

### Loading Workflows in ComfyUI

1. **From JSON files**: Drag and drop any `.json` workflow file into the ComfyUI browser window
2. **From PNG files**: Some workflows are embedded in PNG images - drag the PNG into ComfyUI to load the workflow
3. **Via API**: Use the `/prompt` endpoint to load workflows programmatically

### Downloading Workflows from CivitAI

Use the `download_workflow.py` script:

```bash
# Download from a specific URL
python download_workflow.py https://civitai.com/models/12345

# Search for workflows
python download_workflow.py --search "V07"

# Search for Qwen3-TTS workflows
python download_workflow.py --search "qwen3tts"

# Search for Z-Image workflows
python download_workflow.py --search "z-image"
```

## Qwen3-TTS Workflows

Qwen3-TTS is a text-to-speech model that supports 10 major languages and provides high-quality audio generation.

### Requirements

1. Install the Qwen3-TTS custom node:
   ```bash
   # Using ComfyUI Manager, search for "ComfyUI-Qwen-TTS"
   # Or clone manually:
   git clone https://github.com/flybirdxx/ComfyUI-Qwen-TTS.git custom_nodes/ComfyUI-Qwen-TTS
   ```

2. Download the Qwen3-TTS model:
   - Model: `Qwen3-TTS-12Hz-1.7B-Base`
   - Available on HuggingFace: https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base

### Features

- **10 Languages**: Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian
- **Low Latency**: Streaming generation with as low as 97ms latency
- **Voice Control**: Control tone, emotion, and prosody
- **Natural Language Instructions**: Generate speech from natural language prompts

### Example Usage

1. Load a Qwen3-TTS workflow from the `qwen3tts/` directory
2. Enter your text prompt
3. Select language and voice settings
4. Generate audio output

## Z-Image Workflows

Z-Image is a fast, efficient image generation model optimized for speed and quality.

### Requirements

1. Download the required model files:
   - `zImage_turbo.safetensors` (diffusion model)
   - `zImage_vae.safetensors` (autoencoder)
   - `zImage_textEncoder.safetensors` (Qwen 3B CLIP encoder)

2. Place models in the appropriate directories:
   - Diffusion model: `models/checkpoints/`
   - VAE: `models/vae/`
   - Text encoder: `models/clip/`

### Features

- **Speed**: Generates images in 13-30 seconds on 8GB VRAM
- **Quality**: Photorealistic visuals with sharp textures
- **Efficiency**: Optimized for low VRAM hardware
- **Resolution**: Optimized up to 2K resolution

### Example Usage

1. Load a Z-Image workflow from the `zimage/` directory
2. Enter your text prompt
3. Adjust resolution and sampling settings
4. Generate image

## Finding Workflows

### CivitAI Search Tips

- Search for "V07" to find V07-related workflows
- Search for "qwen3tts" or "qwen tts" for text-to-speech workflows
- Search for "z-image" or "zimage" for Z-Image workflows
- Use tags like "comfyui", "workflow", "template" to find more workflows

### Workflow Types

Workflows can be:
- **JSON files**: Direct workflow definitions
- **PNG files**: Images with embedded workflow metadata
- **Templates**: Reusable workflow templates

## Troubleshooting

### Missing Custom Nodes

If a workflow requires a custom node that's not installed:
1. Check the workflow JSON for node class names
2. Install the required custom node via ComfyUI Manager
3. Restart ComfyUI

### Missing Models

If a workflow references models you don't have:
1. Check the workflow for model filenames
2. Download required models from HuggingFace, CivitAI, or other sources
3. Place models in the correct directories

### Workflow Errors

- Verify all required nodes are installed
- Check that model paths are correct
- Ensure all dependencies are installed
- Review the ComfyUI console for error messages

## Contributing

To add workflows to this directory:
1. Download or create workflow JSON files
2. Place them in the appropriate subdirectory
3. Add a descriptive filename
4. Optionally add a README with usage instructions

# Qwen3-TTS Workflows

This directory contains workflows that use Qwen3-TTS (Text-to-Speech) functionality.

## About Qwen3-TTS

Qwen3-TTS is an advanced text-to-speech model developed by Alibaba's Tongyi Lab. It provides high-quality, multilingual speech synthesis with low latency.

## Setup

### 1. Install Custom Node

Install the ComfyUI-Qwen-TTS custom node:

**Option A: Using ComfyUI Manager**
1. Open ComfyUI Manager
2. Search for "ComfyUI-Qwen-TTS"
3. Click Install

**Option B: Manual Installation**
```bash
cd custom_nodes
git clone https://github.com/flybirdxx/ComfyUI-Qwen-TTS.git
cd ComfyUI-Qwen-TTS
pip install -r requirements.txt
```

### 2. Download Model

Download the Qwen3-TTS model from HuggingFace:
- Model: `Qwen/Qwen3-TTS-12Hz-1.7B-Base`
- URL: https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base

Place the model files in your ComfyUI models directory (typically `models/tts/` or as specified by the custom node).

## Features

- **10 Supported Languages**: Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian
- **Low Latency**: Streaming generation with as low as 97ms latency
- **Voice Control**: Control tone, emotion, and prosody through natural language
- **High Quality**: High-fidelity audio reconstruction

## Using Workflows

1. Load a workflow JSON file from this directory into ComfyUI
2. Configure your text input
3. Select language and voice parameters
4. Generate audio output

## Finding More Workflows

Search CivitAI for Qwen3-TTS workflows:
```bash
python ../search_workflows.py "qwen3tts" --type qwen3tts
```

Or use the download script:
```bash
python ../download_workflow.py --search "qwen3tts"
```

## Troubleshooting

### Custom Node Not Found
- Ensure the custom node is installed in `custom_nodes/ComfyUI-Qwen-TTS`
- Restart ComfyUI after installation

### Model Not Found
- Verify model files are in the correct directory
- Check the custom node documentation for model path requirements

### Audio Generation Errors
- Check that all dependencies are installed
- Verify model files are complete and not corrupted
- Review ComfyUI console for error messages

#!/usr/bin/env python3
"""
Check for missing models referenced in workflows
and compare with available models in ComfyUI
"""

import folder_paths
import json
import sys
import os

def get_available_models():
    """Get all available models from ComfyUI"""
    return {
        "checkpoints": folder_paths.get_filename_list("checkpoints"),
        "vae": folder_paths.get_filename_list("vae"),
    }

def check_workflow_file(workflow_path):
    """Check a workflow JSON file for missing models"""
    try:
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
    except Exception as e:
        print(f"Error reading {workflow_path}: {e}")
        return
    
    available = get_available_models()
    missing = {"checkpoints": [], "vae": []}
    
    # Check all nodes in the workflow
    if "nodes" in workflow:
        for node in workflow["nodes"]:
            if node.get("class_type") == "CheckpointLoaderSimple":
                ckpt_name = node.get("inputs", {}).get("ckpt_name")
                if ckpt_name and ckpt_name not in available["checkpoints"]:
                    missing["checkpoints"].append(ckpt_name)
            
            elif node.get("class_type") == "VAELoader":
                vae_name = node.get("inputs", {}).get("vae_name")
                if vae_name and vae_name not in available["vae"]:
                    missing["vae"].append(vae_name)
    
    return missing, available

def main():
    print("=" * 60)
    print("ComfyUI Model Availability Checker")
    print("=" * 60)
    
    # Show available models
    available = get_available_models()
    print("\n📦 Available Models:")
    print(f"\n  Checkpoints ({len(available['checkpoints'])}):")
    for ckpt in available["checkpoints"]:
        print(f"    ✓ {ckpt}")
    
    print(f"\n  VAEs ({len(available['vae'])}):")
    for vae in available["vae"]:
        print(f"    ✓ {vae}")
    
    # Check specific models mentioned in error
    print("\n" + "=" * 60)
    print("Checking models from error message:")
    print("=" * 60)
    
    missing_ckpt = "SD1.5/V07_v07.safetensors"
    missing_vae = "vae-ft-mse-840000-ema-pruned.safetensors"
    
    print(f"\n  Checkpoint: {missing_ckpt}")
    if missing_ckpt in available["checkpoints"]:
        print(f"    ✓ Found!")
    else:
        print(f"    ✗ NOT FOUND")
        print(f"    Expected location: models/checkpoints/{missing_ckpt}")
        if os.path.exists(f"models/checkpoints/{missing_ckpt}"):
            print(f"    ⚠ File exists but not in cache! Try clearing cache.")
        else:
            print(f"    → You need to download this model")
    
    print(f"\n  VAE: {missing_vae}")
    if missing_vae in available["vae"]:
        print(f"    ✓ Found!")
    else:
        print(f"    ✗ NOT FOUND")
        print(f"    Expected location: models/vae/{missing_vae}")
        if os.path.exists(f"models/vae/{missing_vae}"):
            print(f"    ⚠ File exists but not in cache! Try clearing cache.")
        else:
            print(f"    → You need to download this model")
    
    print("\n" + "=" * 60)
    print("Solutions:")
    print("=" * 60)
    print("\n1. Download missing models:")
    print("   - Place checkpoints in: models/checkpoints/")
    print("   - Place VAEs in: models/vae/")
    print("\n2. Clear cache (if files exist but not detected):")
    print("   python3 clear-model-cache.py")
    print("\n3. Update workflow to use available models:")
    print("   - Replace missing models with ones from the list above")
    print("\n4. Check for extra_model_paths.yaml:")
    print("   - Models might be in additional configured paths")

if __name__ == "__main__":
    main()

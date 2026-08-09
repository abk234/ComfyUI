#!/usr/bin/env python3
"""
Add missing models to ComfyUI-Manager's model-list.json
This will make them appear in the Model Manager UI for download
"""

import json
import os
import sys
import shutil
from datetime import datetime

# Paths
manager_dir = os.path.join(os.path.dirname(__file__), "custom_nodes", "ComfyUI-Manager")
model_list_path = os.path.join(manager_dir, "model-list.json")

def add_models_to_list():
    """Add missing models to the model list"""
    
    if not os.path.exists(model_list_path):
        print(f"Error: model-list.json not found at {model_list_path}")
        return False
    
    # Create backup
    backup_path = model_list_path + f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(model_list_path, backup_path)
    print(f"✓ Created backup: {backup_path}")
    
    # Load existing model list
    with open(model_list_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    models = data.get("models", [])
    
    # Check if models already exist
    existing_filenames = {m.get("filename") for m in models}
    
    new_models = []
    
    # Add VAE model (vae-ft-mse-840000-ema-pruned.safetensors)
    if "vae-ft-mse-840000-ema-pruned.safetensors" not in existing_filenames:
        vae_model = {
            "name": "VAE FT MSE 840000 EMA Pruned",
            "type": "vae",
            "base": "SD1.5",
            "save_path": "vae",
            "description": "Fine-tuned VAE for Stable Diffusion 1.5. Trained for 840,000 steps using MSE loss with emphasis on reconstruction, producing smoother outputs compared to the original VAE.",
            "reference": "https://huggingface.co/stabilityai/sd-vae-ft-mse-original",
            "filename": "vae-ft-mse-840000-ema-pruned.safetensors",
            "url": "https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors?download=true",
            "size": "335MB"
        }
        new_models.append(vae_model)
        print("✓ Added VAE model: vae-ft-mse-840000-ema-pruned.safetensors")
    else:
        print("⚠ VAE model already exists in list")
    
    # Add V07 checkpoint (placeholder - user needs to provide URL)
    v07_filename = "V07_v07.safetensors"
    v07_exists = any(m.get("filename") == v07_filename for m in models)
    
    if not v07_exists:
        print("\n⚠ V07_v07.safetensors not found in model list")
        print("   This model needs a download URL to be added.")
        print("   Please provide:")
        print("   1. Download URL (HuggingFace, Civitai, etc.)")
        print("   2. Model size")
        print("   3. Reference link (optional)")
        
        add_v07 = input("\nDo you want to add V07_v07.safetensors now? (y/n): ").strip().lower()
        
        if add_v07 == 'y':
            url = input("Enter download URL: ").strip()
            if not url:
                print("⚠ No URL provided, skipping V07 model")
            else:
                size = input("Enter model size (e.g., '2.5GB'): ").strip() or "Unknown"
                reference = input("Enter reference URL (optional, press Enter to skip): ").strip() or ""
                
                v07_model = {
                    "name": "V07 v07",
                    "type": "checkpoint",
                    "base": "SD1.5",
                    "save_path": "checkpoints/SD1.5",
                    "description": "V07 v07 checkpoint model for Stable Diffusion 1.5",
                    "reference": reference or "https://huggingface.co",
                    "filename": v07_filename,
                    "url": url,
                    "size": size
                }
                new_models.append(v07_model)
                print("✓ Added V07 checkpoint model")
    else:
        print("⚠ V07 model already exists in list")
    
    # Add new models to the list
    if new_models:
        models.extend(new_models)
        data["models"] = models
        
        # Save updated list
        with open(model_list_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Added {len(new_models)} model(s) to model-list.json")
        print(f"✓ Total models in list: {len(models)}")
        return True
    else:
        print("\n✓ No new models to add")
        return False

def update_cache():
    """Update the ComfyUI-Manager cache"""
    try:
        print("\nUpdating ComfyUI-Manager cache...")
        sys.path.insert(0, os.path.join(manager_dir, 'glob'))
        import manager_util
        
        cache_dir = manager_util.cache_dir
        manager_path = manager_util.comfyui_manager_path
        local_file = os.path.join(manager_path, 'model-list.json')
        
        channel_url = 'https://raw.githubusercontent.com/ltdrdata/ComfyUI-Manager/main'
        uri = channel_url + '/model-list.json'
        cache_uri = str(manager_util.simple_hash(uri)) + '_model-list.json'
        cache_path = os.path.join(cache_dir, cache_uri)
        
        os.makedirs(cache_dir, exist_ok=True)
        
        with open(local_file, 'r') as f:
            local_data = json.load(f)
        
        with open(cache_path, 'w') as f:
            json.dump(local_data, f, indent=2)
        
        import time
        os.utime(cache_path, (time.time(), time.time()))
        
        print(f"✓ Cache updated: {cache_path}")
        return True
    except Exception as e:
        print(f"⚠ Could not update cache automatically: {e}")
        print("   You can run: python3 update-model-cache.py")
        return False

def main():
    print("=" * 60)
    print("Add Missing Models to ComfyUI-Manager")
    print("=" * 60)
    
    if not os.path.exists(manager_dir):
        print(f"Error: ComfyUI-Manager not found at {manager_dir}")
        print("   Make sure ComfyUI-Manager is installed")
        return
    
    if add_models_to_list():
        update_cache()
        print("\n" + "=" * 60)
        print("✓ Success! Models added to Model Manager")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Restart ComfyUI")
        print("2. Open the Model Manager in the UI")
        print("3. You should now see the new models available for download")
    else:
        print("\nNo changes made")

if __name__ == "__main__":
    main()

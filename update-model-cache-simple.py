#!/usr/bin/env python3
"""
Simple script to update ComfyUI-Manager cache
Updates the cache so new models appear in the Model Manager UI
"""

import json
import os
import time
import hashlib

def simple_hash(text):
    """Simple hash function for cache key"""
    return hashlib.md5(text.encode()).hexdigest()

# Paths
base_dir = os.path.dirname(os.path.abspath(__file__))
manager_dir = os.path.join(base_dir, "custom_nodes", "ComfyUI-Manager")
model_list_path = os.path.join(manager_dir, "model-list.json")

# Try to find cache directory
cache_dir = None
possible_cache_dirs = [
    os.path.join(os.path.expanduser("~"), ".cache", "comfyui-manager"),
    os.path.join(os.path.expanduser("~"), ".cache", "ComfyUI-Manager"),
    os.path.join(base_dir, ".cache", "comfyui-manager"),
]

for dir_path in possible_cache_dirs:
    if os.path.exists(dir_path):
        cache_dir = dir_path
        break

if not cache_dir:
    # Create cache directory
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "comfyui-manager")
    os.makedirs(cache_dir, exist_ok=True)
    print(f"Created cache directory: {cache_dir}")

# Channel URL for cache key
channel_url = 'https://raw.githubusercontent.com/ltdrdata/ComfyUI-Manager/main'
uri = channel_url + '/model-list.json'
cache_uri = simple_hash(uri) + '_model-list.json'
cache_path = os.path.join(cache_dir, cache_uri)

print(f"Updating cache file: {cache_path}")

# Load local model-list.json
if not os.path.exists(model_list_path):
    print(f"Error: model-list.json not found at {model_list_path}")
    exit(1)

with open(model_list_path, 'r', encoding='utf-8') as f:
    local_data = json.load(f)

# Write to cache file
with open(cache_path, 'w', encoding='utf-8') as f:
    json.dump(local_data, f, indent=2, ensure_ascii=False)

# Update file timestamp to make it "fresh"
os.utime(cache_path, (time.time(), time.time()))

print(f"✓ Cache file updated successfully")
print(f"  Cache file: {cache_path}")
print(f"  Models in cache: {len(local_data.get('models', []))}")

# Verify
with open(cache_path, 'r', encoding='utf-8') as f:
    cached_data = json.load(f)
    vae_models = [m for m in cached_data.get('models', []) if m.get('filename') == 'vae-ft-mse-840000-ema-pruned.safetensors']
    v07_models = [m for m in cached_data.get('models', []) if m.get('filename') == 'V07_v07.safetensors']
    print(f"  VAE model in cache: {len(vae_models) > 0}")
    print(f"  V07 model in cache: {len(v07_models) > 0}")

print("\n✓ Cache updated! Restart ComfyUI to see the models in Model Manager")

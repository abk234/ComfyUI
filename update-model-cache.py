#!/usr/bin/env python3
"""
Update ComfyUI Manager cache with local model-list.json
This ensures the Noosphere model appears in ComfyUI Manager
"""

import sys
import os
import json
import time

# Add ComfyUI-Manager glob to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_nodes/ComfyUI-Manager/glob'))

import manager_util

# Get paths
cache_dir = manager_util.cache_dir
manager_path = manager_util.comfyui_manager_path
local_file = os.path.join(manager_path, 'model-list.json')

# Channel URL for cache key
channel_url = 'https://raw.githubusercontent.com/ltdrdata/ComfyUI-Manager/main'
uri = channel_url + '/model-list.json'
cache_uri = str(manager_util.simple_hash(uri)) + '_model-list.json'
cache_path = os.path.join(cache_dir, cache_uri)

print(f"Updating cache file: {cache_path}")

# Ensure cache directory exists
os.makedirs(cache_dir, exist_ok=True)

# Load local model-list.json
with open(local_file, 'r') as f:
    local_data = json.load(f)

# Check if Noosphere is in local file
noosphere = [m for m in local_data.get('models', []) if 'noosphere' in m.get('name', '').lower()]
print(f"Local file has {len(noosphere)} Noosphere model(s)")

# Write to cache file
with open(cache_path, 'w') as f:
    json.dump(local_data, f, indent=2)

# Update file timestamp to make it "fresh"
os.utime(cache_path, (time.time(), time.time()))

print(f"✓ Cache file updated successfully")
print(f"  Cache file: {cache_path}")
print(f"  Models in cache: {len(local_data.get('models', []))}")

# Verify
with open(cache_path, 'r') as f:
    cached_data = json.load(f)
    cached_noosphere = [m for m in cached_data.get('models', []) if 'noosphere' in m.get('name', '').lower()]
    print(f"  Noosphere in cache: {len(cached_noosphere)}")
    if cached_noosphere:
        print(f"  Model name: {cached_noosphere[0].get('name')}")

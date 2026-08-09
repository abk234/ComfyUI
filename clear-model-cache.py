#!/usr/bin/env python3
"""
Clear ComfyUI model file list cache
This forces ComfyUI to rescan the model directories on next startup
"""

import folder_paths
import os

print("Clearing ComfyUI model file list cache...")

# Clear the filename list cache
folder_paths.filename_list_cache.clear()
print("✓ Cleared filename_list_cache")

# Clear the cache helper
folder_paths.cache_helper.clear()
print("✓ Cleared cache_helper")

# Verify by checking a folder
print("\nTesting cache clear...")
files = folder_paths.get_filename_list("checkpoints")
print(f"✓ Found {len(files)} checkpoint files after cache clear:")
for f in files[:5]:
    print(f"  - {f}")

print("\n✓ Cache cleared successfully!")
print("  Restart ComfyUI to see updated file lists in the UI")

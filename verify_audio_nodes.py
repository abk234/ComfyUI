#!/usr/bin/env python3
"""
Verification script to check if audio nodes are properly installed and available.
Run this before starting ComfyUI to ensure all dependencies are met.
"""

import sys
import asyncio
import importlib

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("=" * 70)
    print("Checking Dependencies")
    print("=" * 70)
    
    required_deps = {
        'av': 'PyAV (av)',
        'torchaudio': 'torchaudio',
        'torch': 'PyTorch',
    }
    
    all_ok = True
    for module_name, display_name in required_deps.items():
        try:
            importlib.import_module(module_name)
            print(f"✓ {display_name} is installed")
        except ImportError:
            print(f"✗ {display_name} is NOT installed")
            all_ok = False
    
    print()
    return all_ok

async def check_nodes():
    """Check if audio nodes are properly registered."""
    print("=" * 70)
    print("Checking Audio Nodes")
    print("=" * 70)
    
    sys.path.insert(0, '.')
    
    try:
        import nodes
        
        # Load built-in extra nodes
        print("\nLoading built-in extra nodes...")
        failed = await nodes.init_builtin_extra_nodes()
        if failed:
            print(f"⚠ Warning: Some nodes failed to load: {failed}")
        
        # Check audio nodes
        audio_nodes = ['LoadAudio', 'PreviewAudio', 'SaveAudio']
        all_found = True
        
        print("\nChecking for audio nodes in NODE_CLASS_MAPPINGS:")
        for node_name in audio_nodes:
            if node_name in nodes.NODE_CLASS_MAPPINGS:
                node_class = nodes.NODE_CLASS_MAPPINGS[node_name]
                try:
                    schema = node_class.GET_SCHEMA()
                    print(f"  ✓ {node_name}")
                    print(f"    - Display Name: {schema.display_name}")
                    print(f"    - Category: {schema.category}")
                except Exception as e:
                    print(f"  ⚠ {node_name} (schema error: {e})")
            else:
                print(f"  ✗ {node_name} is NOT registered")
                all_found = False
        
        print()
        return all_found
        
    except Exception as e:
        print(f"✗ Error loading nodes: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main verification function."""
    print("\n" + "=" * 70)
    print("ComfyUI Audio Nodes Verification")
    print("=" * 70 + "\n")
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n❌ Some dependencies are missing!")
        print("Please install missing dependencies:")
        print("  pip install av>=14.2.0 torchaudio")
        print()
        return False
    
    # Check nodes
    nodes_ok = asyncio.run(check_nodes())
    
    print("=" * 70)
    if deps_ok and nodes_ok:
        print("✅ All checks passed! Audio nodes should be available in ComfyUI.")
        print("\nIf you still see errors in ComfyUI:")
        print("  1. Restart the ComfyUI server completely")
        print("  2. Clear your browser cache")
        print("  3. Hard refresh the page (Ctrl+Shift+R or Cmd+Shift+R)")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    print("=" * 70 + "\n")
    
    return deps_ok and nodes_ok

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

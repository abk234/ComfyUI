#!/usr/bin/env python3
"""
Test script to simulate what happens when ComfyUI validates a workflow
and shows missing models with download links from Model Manager
"""

import json
import folder_paths
import os

def test_workflow_validation(workflow_path):
    """Simulate workflow validation and check missing models"""
    
    print("=" * 70)
    print("Testing Workflow: 6-DetailerWildcard.json")
    print("=" * 70)
    
    # Load workflow
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    
    # Get available models
    available_checkpoints = folder_paths.get_filename_list('checkpoints')
    available_vaes = folder_paths.get_filename_list('vae')
    
    # Load Model Manager list
    model_list_path = 'custom_nodes/ComfyUI-Manager/model-list.json'
    with open(model_list_path, 'r') as f:
        model_list_data = json.load(f)
    
    # Create lookup by filename
    model_manager_lookup = {}
    for model in model_list_data.get('models', []):
        filename = model.get('filename', '')
        model_manager_lookup[filename] = model
        # Also index by basename for partial matches
        basename = os.path.basename(filename)
        if basename not in model_manager_lookup:
            model_manager_lookup[basename] = model
    
    # Extract models from workflow
    missing_models = []
    
    # Check workflow node
    for node in workflow.get('nodes', []):
        if node.get('type') == 'workflow>MAKE_BASIC_PIPE':
            widgets = node.get('widgets_values', [])
            if len(widgets) >= 2:
                vae_name = widgets[0]
                ckpt_name = widgets[1]
                
                # Check VAE
                if vae_name not in available_vaes:
                    missing_models.append({
                        'type': 'vae',
                        'name': vae_name,
                        'available': False,
                        'in_manager': vae_name in model_manager_lookup or os.path.basename(vae_name) in model_manager_lookup
                    })
                
                # Check checkpoint
                if ckpt_name not in available_checkpoints:
                    missing_models.append({
                        'type': 'checkpoint',
                        'name': ckpt_name,
                        'available': False,
                        'in_manager': ckpt_name in model_manager_lookup or os.path.basename(ckpt_name) in model_manager_lookup
                    })
    
    print("\n📋 Validation Results:")
    print("-" * 70)
    
    if not missing_models:
        print("✅ All models are available!")
        return
    
    print(f"⚠️  Found {len(missing_models)} missing model(s):\n")
    
    for i, model in enumerate(missing_models, 1):
        print(f"{i}. {model['type'].upper()}: {model['name']}")
        print(f"   Status: {'✗ Missing from filesystem'}")
        
        # Check if in Model Manager
        model_info = None
        if model['name'] in model_manager_lookup:
            model_info = model_manager_lookup[model['name']]
        elif os.path.basename(model['name']) in model_manager_lookup:
            model_info = model_manager_lookup[os.path.basename(model['name'])]
        
        if model_info:
            print(f"   Model Manager: ✅ Found")
            print(f"   Name: {model_info.get('name', 'N/A')}")
            url = model_info.get('url', '')
            if url and url != 'PLACEHOLDER_UPDATE_WITH_ACTUAL_DOWNLOAD_URL':
                print(f"   Download URL: ✅ Available")
                print(f"   URL: {url[:80]}...")
                print(f"   Size: {model_info.get('size', 'Unknown')}")
            else:
                print(f"   Download URL: ⚠️  Placeholder (needs update)")
                print(f"   Action: Update URL in model-list.json")
        else:
            print(f"   Model Manager: ❌ NOT found")
            print(f"   Action: Add to model-list.json")
        print()
    
    print("=" * 70)
    print("What happens in ComfyUI:")
    print("=" * 70)
    print("""
1. When you open this workflow, ComfyUI validates it
2. Validation detects missing models and creates 'value_not_in_list' errors
3. ComfyUI-Manager checks if missing models are in model-list.json
4. If found, they appear in the Model Manager UI with download links
5. You can click 'Install' or use the download button to get them

For this workflow:
""")
    
    for model in missing_models:
        model_info = None
        if model['name'] in model_manager_lookup:
            model_info = model_manager_lookup[model['name']]
        elif os.path.basename(model['name']) in model_manager_lookup:
            model_info = model_manager_lookup[os.path.basename(model['name'])]
        
        if model_info:
            url = model_info.get('url', '')
            if url and url != 'PLACEHOLDER_UPDATE_WITH_ACTUAL_DOWNLOAD_URL':
                print(f"  ✅ {model['name']} - Will show with download link")
            else:
                print(f"  ⚠️  {model['name']} - Will show but needs URL update")
        else:
            print(f"  ❌ {model['name']} - Won't show (not in Model Manager)")
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("1. Restart ComfyUI to load updated model-list.json")
    print("2. Open the workflow: 6-DetailerWildcard.json")
    print("3. Check the Model Manager (filter: 'In Workflow')")
    print("4. Missing models should appear with download links")
    print("5. Click 'Install' to download them automatically")

if __name__ == "__main__":
    workflow_path = "custom_nodes/comfyui-impact-pack/example_workflows/6-DetailerWildcard.json"
    if os.path.exists(workflow_path):
        test_workflow_validation(workflow_path)
    else:
        print(f"Error: Workflow not found at {workflow_path}")

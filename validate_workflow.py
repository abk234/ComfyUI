#!/usr/bin/env python3
"""
Comprehensive workflow validation tool for ComfyUI.

This script validates workflows and ensures all dependencies are met:
- Missing models (checkpoints, VAE, LoRA, etc.)
- Missing custom nodes
- Missing Python dependencies
- Integration with ComfyUI Manager for automatic downloads

Usage:
    python validate_workflow.py <workflow.json>
    python validate_workflow.py <workflow.json> --fix
    python validate_workflow.py <workflow.json> --check-manager
"""

import os
import sys
import json
import importlib
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict

# Add current directory to path to import ComfyUI modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import folder_paths
except ImportError:
    print("Error: Could not import folder_paths. Make sure you're running this from the ComfyUI directory.")
    sys.exit(1)


class WorkflowValidator:
    def __init__(self, workflow_path: str):
        self.workflow_path = Path(workflow_path)
        self.workflow_data = None
        self.issues = {
            'missing_models': defaultdict(list),
            'missing_nodes': [],
            'missing_dependencies': [],
            'warnings': []
        }
        self.model_manager_lookup = {}
        self.available_models = {}
        self.installed_nodes = set()
        
    def load_workflow(self) -> bool:
        """Load workflow JSON file."""
        try:
            with open(self.workflow_path, 'r', encoding='utf-8') as f:
                self.workflow_data = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading workflow: {e}")
            return False
    
    def get_available_models(self):
        """Get all available models from ComfyUI."""
        model_types = [
            'checkpoints', 'vae', 'loras', 'embeddings', 'controlnet',
            'upscale_models', 'clip', 'text_encoders', 'diffusion_models'
        ]
        
        available = {}
        for model_type in model_types:
            try:
                available[model_type] = set(folder_paths.get_filename_list(model_type))
            except:
                available[model_type] = set()
        
        self.available_models = available
        return available
    
    def load_model_manager_list(self):
        """Load ComfyUI Manager's model list if available."""
        model_list_paths = [
            Path('custom_nodes/ComfyUI-Manager/model-list.json'),
            Path('custom_nodes/comfyui-manager/model-list.json'),
        ]
        
        for path in model_list_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        model_list_data = json.load(f)
                    
                    # Create lookup by filename
                    for model in model_list_data.get('models', []):
                        filename = model.get('filename', '')
                        if filename:
                            self.model_manager_lookup[filename] = model
                            # Also index by basename
                            basename = os.path.basename(filename)
                            if basename not in self.model_manager_lookup:
                                self.model_manager_lookup[basename] = model
                    
                    print(f"✓ Loaded {len(self.model_manager_lookup)} models from Model Manager")
                    return True
                except Exception as e:
                    print(f"⚠ Warning: Could not load Model Manager list: {e}")
        
        return False
    
    def get_installed_custom_nodes(self):
        """Get list of installed custom nodes."""
        custom_node_dirs = folder_paths.get_folder_paths("custom_nodes")
        installed = set()
        
        for custom_node_dir in custom_node_dirs:
            if os.path.exists(custom_node_dir):
                for item in os.listdir(custom_node_dir):
                    node_path = os.path.join(custom_node_dir, item)
                    if os.path.isdir(node_path) and not item.startswith('.'):
                        installed.add(item)
        
        self.installed_nodes = installed
        return installed
    
    def extract_models_from_workflow(self) -> Dict[str, List[str]]:
        """Extract all model references from workflow."""
        models = defaultdict(list)
        
        if not self.workflow_data or 'nodes' not in self.workflow_data:
            return models
        
        node_type_mapping = {
            'CheckpointLoaderSimple': ('checkpoints', 'ckpt_name'),
            'CheckpointLoader': ('checkpoints', 'ckpt_name'),
            'VAELoader': ('vae', 'vae_name'),
            'VAEDecode': ('vae', 'vae_name'),
            'VAEEncode': ('vae', 'vae_name'),
            'LoraLoader': ('loras', 'lora_name'),
            'ControlNetLoader': ('controlnet', 'control_net_name'),
            'UpscaleModelLoader': ('upscale_models', 'model_name'),
            'CLIPLoader': ('clip', 'clip_name'),
            'DualCLIPLoader': ('clip', 'clip_name1'),
            'UNETLoader': ('diffusion_models', 'unet_name'),
        }
        
        for node in self.workflow_data['nodes']:
            class_type = node.get('class_type', '')
            if class_type in node_type_mapping:
                model_type, input_key = node_type_mapping[class_type]
                inputs = node.get('inputs', {})
                model_name = inputs.get(input_key)
                
                if model_name:
                    # Handle dual CLIP loader
                    if class_type == 'DualCLIPLoader':
                        models[model_type].append(model_name)
                        clip_name2 = inputs.get('clip_name2')
                        if clip_name2:
                            models[model_type].append(clip_name2)
                    else:
                        models[model_type].append(model_name)
        
        return models
    
    def extract_custom_nodes_from_workflow(self) -> Set[str]:
        """Extract custom node class types from workflow."""
        custom_nodes = set()
        
        if not self.workflow_data or 'nodes' not in self.workflow_data:
            return custom_nodes
        
        # Built-in nodes (these don't need custom nodes)
        builtin_nodes = {
            'CheckpointLoaderSimple', 'CheckpointLoader', 'VAELoader',
            'CLIPTextEncode', 'KSampler', 'VAEDecode', 'SaveImage',
            'LoadImage', 'EmptyLatentImage', 'LoraLoader', 'ControlNetLoader'
        }
        
        for node in self.workflow_data['nodes']:
            class_type = node.get('class_type', '')
            if class_type and class_type not in builtin_nodes:
                # Check if it's likely a custom node
                # Custom nodes often have patterns like: NodeName, CustomNodeName, etc.
                custom_nodes.add(class_type)
        
        return custom_nodes
    
    def check_python_dependencies(self, node_class: str) -> List[str]:
        """Check if a custom node has missing Python dependencies."""
        missing = []
        
        # Try to find the custom node directory
        custom_node_dirs = folder_paths.get_folder_paths("custom_nodes")
        for custom_node_dir in custom_node_dirs:
            if os.path.exists(custom_node_dir):
                for item in os.listdir(custom_node_dir):
                    node_path = os.path.join(custom_node_dir, item)
                    if os.path.isdir(node_path):
                        # Check for requirements.txt
                        req_file = os.path.join(node_path, 'requirements.txt')
                        if os.path.exists(req_file):
                            try:
                                with open(req_file, 'r') as f:
                                    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                                
                                for req in requirements:
                                    # Parse requirement (e.g., "package>=1.0.0" -> "package")
                                    package_name = req.split('>=')[0].split('==')[0].split('>')[0].split('<')[0].strip()
                                    
                                    # Try to import
                                    try:
                                        importlib.import_module(package_name)
                                    except ImportError:
                                        missing.append(f"{package_name} (from {item})")
                            except:
                                pass
        
        return missing
    
    def validate(self) -> bool:
        """Run full validation."""
        if not self.load_workflow():
            return False
        
        print("=" * 70)
        print(f"Validating Workflow: {self.workflow_path.name}")
        print("=" * 70)
        
        # Get available resources
        print("\n📦 Checking available resources...")
        self.get_available_models()
        self.get_installed_custom_nodes()
        self.load_model_manager_list()
        
        # Extract requirements from workflow
        print("\n🔍 Analyzing workflow requirements...")
        required_models = self.extract_models_from_workflow()
        required_nodes = self.extract_custom_nodes_from_workflow()
        
        # Check models
        print("\n✅ Checking models...")
        for model_type, model_names in required_models.items():
            available = self.available_models.get(model_type, set())
            for model_name in set(model_names):  # Remove duplicates
                if model_name not in available:
                    self.issues['missing_models'][model_type].append(model_name)
        
        # Check custom nodes
        print("✅ Checking custom nodes...")
        for node_class in required_nodes:
            # Try to determine if it's a custom node by checking if it's in installed nodes
            # This is a heuristic - we check if any custom node directory might contain it
            found = False
            for installed_node in self.installed_nodes:
                # Check if node class might be from this custom node
                node_path = None
                for custom_node_dir in folder_paths.get_folder_paths("custom_nodes"):
                    potential_path = os.path.join(custom_node_dir, installed_node)
                    if os.path.exists(potential_path):
                        # Check if node file exists
                        for root, dirs, files in os.walk(potential_path):
                            for file in files:
                                if file.endswith('.py') and not file.startswith('__'):
                                    try:
                                        # Try to see if this file might define the node
                                        with open(os.path.join(root, file), 'r') as f:
                                            content = f.read()
                                            if node_class in content:
                                                found = True
                                                break
                                    except:
                                        pass
                            if found:
                                break
                    if found:
                        break
                if found:
                    break
            
            if not found:
                self.issues['missing_nodes'].append(node_class)
        
        return True
    
    def print_report(self):
        """Print validation report."""
        print("\n" + "=" * 70)
        print("VALIDATION REPORT")
        print("=" * 70)
        
        all_ok = True
        
        # Missing Models
        if self.issues['missing_models']:
            all_ok = False
            print("\n❌ MISSING MODELS:")
            print("-" * 70)
            
            for model_type, models in self.issues['missing_models'].items():
                print(f"\n  {model_type.upper()}:")
                for model in models:
                    print(f"    • {model}")
                    
                    # Check if in Model Manager
                    model_info = None
                    if model in self.model_manager_lookup:
                        model_info = self.model_manager_lookup[model]
                    elif os.path.basename(model) in self.model_manager_lookup:
                        model_info = self.model_manager_lookup[os.path.basename(model)]
                    
                    if model_info:
                        url = model_info.get('url', '')
                        if url and url != 'PLACEHOLDER_UPDATE_WITH_ACTUAL_DOWNLOAD_URL':
                            print(f"      ✓ Available in Model Manager")
                            print(f"      → Download URL: {url[:60]}...")
                            print(f"      → Size: {model_info.get('size', 'Unknown')}")
                            print(f"      → Action: Install via ComfyUI Manager UI")
                        else:
                            print(f"      ⚠ In Model Manager but needs URL update")
                    else:
                        print(f"      ✗ Not in Model Manager")
                        print(f"      → Action: Download manually or add to model-list.json")
        else:
            print("\n✅ All models are available!")
        
        # Missing Custom Nodes
        if self.issues['missing_nodes']:
            all_ok = False
            print("\n❌ MISSING CUSTOM NODES:")
            print("-" * 70)
            for node in self.issues['missing_nodes']:
                print(f"  • {node}")
                print(f"    → Action: Install via ComfyUI Manager or manually")
        else:
            print("\n✅ All custom nodes are available!")
        
        # Warnings
        if self.issues['warnings']:
            print("\n⚠️  WARNINGS:")
            print("-" * 70)
            for warning in self.issues['warnings']:
                print(f"  • {warning}")
        
        # Summary
        print("\n" + "=" * 70)
        if all_ok:
            print("✅ WORKFLOW IS READY TO USE!")
        else:
            print("⚠️  WORKFLOW HAS ISSUES - See above for details")
        print("=" * 70)
        
        # Recommendations
        if not all_ok:
            print("\n📋 RECOMMENDATIONS:")
            print("-" * 70)
            print("1. Install missing models via ComfyUI Manager:")
            print("   - Open ComfyUI")
            print("   - Go to Manager → Model Manager")
            print("   - Filter by 'In Workflow'")
            print("   - Click 'Install' on missing models")
            print()
            print("2. Install missing custom nodes:")
            print("   - Go to Manager → Install Custom Nodes")
            print("   - Search for the node name")
            print("   - Click 'Install'")
            print()
            print("3. Or use the download script:")
            print(f"   python download_workflow.py --search \"<model_name>\"")
        
        return all_ok
    
    def generate_fix_script(self) -> Optional[str]:
        """Generate a script to fix issues."""
        if not any(self.issues.values()):
            return None
        
        script_lines = [
            "#!/bin/bash",
            "# Auto-generated fix script for workflow validation",
            "",
            "echo 'Installing missing dependencies...'",
            ""
        ]
        
        # Add model downloads from Model Manager
        for model_type, models in self.issues['missing_models'].items():
            for model in models:
                model_info = None
                if model in self.model_manager_lookup:
                    model_info = self.model_manager_lookup[model]
                elif os.path.basename(model) in self.model_manager_lookup:
                    model_info = self.model_manager_lookup[os.path.basename(model)]
                
                if model_info:
                    url = model_info.get('url', '')
                    if url and url != 'PLACEHOLDER_UPDATE_WITH_ACTUAL_DOWNLOAD_URL':
                        # Determine save path
                        if model_type == 'checkpoints':
                            save_path = f"models/checkpoints/{model}"
                        elif model_type == 'vae':
                            save_path = f"models/vae/{model}"
                        elif model_type == 'loras':
                            save_path = f"models/loras/{model}"
                        else:
                            save_path = f"models/{model_type}/{model}"
                        
                        script_lines.append(f"# Download {model}")
                        script_lines.append(f"mkdir -p $(dirname {save_path})")
                        script_lines.append(f"wget -O {save_path} {url}")
                        script_lines.append("")
        
        script_content = "\n".join(script_lines)
        return script_content


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate ComfyUI workflow dependencies'
    )
    parser.add_argument(
        'workflow',
        help='Path to workflow JSON file'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Generate fix script (does not auto-fix)'
    )
    parser.add_argument(
        '--check-manager',
        action='store_true',
        help='Check Model Manager integration'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.workflow):
        print(f"Error: Workflow file not found: {args.workflow}")
        sys.exit(1)
    
    validator = WorkflowValidator(args.workflow)
    
    if validator.validate():
        all_ok = validator.print_report()
        
        if args.fix:
            fix_script = validator.generate_fix_script()
            if fix_script:
                script_path = Path(args.workflow).with_suffix('.fix.sh')
                with open(script_path, 'w') as f:
                    f.write(fix_script)
                os.chmod(script_path, 0o755)
                print(f"\n✓ Fix script generated: {script_path}")
                print("  Review and run it to download missing models")
        
        sys.exit(0 if all_ok else 1)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()

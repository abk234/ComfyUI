#!/usr/bin/env python3
"""
Fix workflow by replacing missing models with available ones
or providing suggestions
"""

import folder_paths
import json
import sys
import os
import shutil
from pathlib import Path

def get_available_models():
    """Get all available models from ComfyUI"""
    return {
        "checkpoints": folder_paths.get_filename_list("checkpoints"),
        "vae": folder_paths.get_filename_list("vae"),
    }

def find_similar_model(target, available_list):
    """Find a similar model name from available list"""
    target_lower = target.lower()
    target_base = os.path.basename(target).lower()
    
    # Try exact match first
    for model in available_list:
        if model.lower() == target_lower:
            return model
    
    # Try basename match
    for model in available_list:
        if os.path.basename(model).lower() == target_base:
            return model
    
    # Try partial match
    for model in available_list:
        if target_base in model.lower() or model.lower() in target_base:
            return model
    
    return None

def fix_workflow(workflow_path, dry_run=True):
    """Fix a workflow by replacing missing models"""
    try:
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
    except Exception as e:
        print(f"Error reading {workflow_path}: {e}")
        return False
    
    available = get_available_models()
    changes = []
    fixed = False
    
    # Check all nodes in the workflow
    if "nodes" in workflow:
        for node in workflow["nodes"]:
            if node.get("class_type") == "CheckpointLoaderSimple":
                ckpt_name = node.get("inputs", {}).get("ckpt_name")
                if ckpt_name and ckpt_name not in available["checkpoints"]:
                    similar = find_similar_model(ckpt_name, available["checkpoints"])
                    if similar:
                        if not dry_run:
                            node["inputs"]["ckpt_name"] = similar
                        changes.append(f"Checkpoint: {ckpt_name} → {similar}")
                        fixed = True
                    else:
                        print(f"⚠ No similar checkpoint found for: {ckpt_name}")
                        print(f"  Available: {', '.join(available['checkpoints'])}")
            
            elif node.get("class_type") == "VAELoader":
                vae_name = node.get("inputs", {}).get("vae_name")
                if vae_name and vae_name not in available["vae"]:
                    similar = find_similar_model(vae_name, available["vae"])
                    if similar:
                        if not dry_run:
                            node["inputs"]["vae_name"] = similar
                        changes.append(f"VAE: {vae_name} → {similar}")
                        fixed = True
                    else:
                        print(f"⚠ No similar VAE found for: {vae_name}")
                        print(f"  Available: {', '.join(available['vae'])}")
    
    if changes:
        print(f"\n{'Would make' if dry_run else 'Made'} the following changes:")
        for change in changes:
            print(f"  • {change}")
        
        if not dry_run:
            # Create backup
            backup_path = workflow_path + ".backup"
            shutil.copy2(workflow_path, backup_path)
            print(f"\n✓ Backup created: {backup_path}")
            
            # Save fixed workflow
            with open(workflow_path, 'w') as f:
                json.dump(workflow, f, indent=2)
            print(f"✓ Fixed workflow saved: {workflow_path}")
        else:
            print(f"\n⚠ DRY RUN - No changes made. Run with --apply to apply changes.")
    
    return fixed

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fix workflow models")
    parser.add_argument("workflow", help="Path to workflow JSON file")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    args = parser.parse_args()
    
    if not os.path.exists(args.workflow):
        print(f"Error: Workflow file not found: {args.workflow}")
        sys.exit(1)
    
    print(f"Analyzing workflow: {args.workflow}")
    fix_workflow(args.workflow, dry_run=not args.apply)

if __name__ == "__main__":
    main()

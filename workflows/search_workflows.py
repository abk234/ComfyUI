#!/usr/bin/env python3
"""
Search and download ComfyUI workflows from CivitAI.

This script provides an interactive way to search for workflows
and download them, with special support for Qwen3-TTS and Z-Image workflows.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import download_workflow
sys.path.insert(0, str(Path(__file__).parent.parent))

from download_workflow import (
    search_civitai_models,
    download_workflow_from_url,
    WORKFLOWS_DIR
)


def search_and_download(query: str, workflow_type: str = None):
    """Search for workflows and provide interactive download."""
    search_query = query
    
    # Enhance search query based on workflow type
    if workflow_type == "qwen3tts":
        search_query = f"{query} qwen3tts qwen tts"
    elif workflow_type == "zimage":
        search_query = f"{query} z-image zimage"
    
    print(f"Searching CivitAI for: {search_query}")
    results = search_civitai_models(search_query, limit=20)
    
    if not results:
        print("No results found. Try a different search term.")
        return
    
    # Filter results that might contain workflows
    workflow_candidates = []
    for model in results:
        model_type = model.get('type', '').lower()
        model_name = model.get('name', '').lower()
        model_tags = [tag.get('name', '').lower() for tag in model.get('tags', [])]
        
        # Look for workflow-related keywords
        workflow_keywords = ['workflow', 'comfyui', 'template', 'json', 'png']
        has_workflow_keyword = any(
            keyword in model_name or 
            any(keyword in tag for tag in model_tags)
            for keyword in workflow_keywords
        )
        
        if has_workflow_keyword or model_type in ['other', 'unknown']:
            workflow_candidates.append(model)
    
    if not workflow_candidates:
        print("No workflow-related results found.")
        return
    
    print(f"\nFound {len(workflow_candidates)} potential workflow(s):\n")
    for i, model in enumerate(workflow_candidates, 1):
        model_id = model.get('id')
        model_name = model.get('name', 'Unknown')
        model_url = f"https://civitai.com/models/{model_id}"
        model_type = model.get('type', 'Unknown')
        stats = model.get('stats', {})
        download_count = stats.get('downloadCount', 0)
        
        print(f"{i}. {model_name}")
        print(f"   URL: {model_url}")
        print(f"   Type: {model_type}")
        print(f"   Downloads: {download_count:,}")
        print()
    
    while True:
        choice = input(
            "Enter the number(s) to download (comma-separated), 'a' for all, or 'q' to quit: "
        ).strip()
        
        if choice.lower() == 'q':
            return
        elif choice.lower() == 'a':
            # Download all
            for model in workflow_candidates:
                model_url = f"https://civitai.com/models/{model['id']}"
                print(f"\n{'='*60}")
                print(f"Downloading: {model['name']}")
                print('='*60)
                download_workflow_from_url(model_url)
            break
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                valid_indices = [idx for idx in indices if 0 <= idx < len(workflow_candidates)]
                
                if not valid_indices:
                    print("Invalid selection. Please try again.")
                    continue
                
                for idx in valid_indices:
                    model = workflow_candidates[idx]
                    model_url = f"https://civitai.com/models/{model['id']}"
                    print(f"\n{'='*60}")
                    print(f"Downloading: {model['name']}")
                    print('='*60)
                    download_workflow_from_url(model_url)
                break
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas, 'a' for all, or 'q' to quit.")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Search and download ComfyUI workflows from CivitAI'
    )
    parser.add_argument(
        'query',
        nargs='?',
        help='Search query (e.g., "V07", "qwen3tts", "z-image")'
    )
    parser.add_argument(
        '--type',
        choices=['qwen3tts', 'zimage', 'all'],
        default='all',
        help='Workflow type filter'
    )
    parser.add_argument(
        '--workflows-dir',
        default=str(WORKFLOWS_DIR),
        help='Directory to save workflows'
    )
    
    args = parser.parse_args()
    
    if not args.query:
        # Interactive mode
        print("ComfyUI Workflow Search and Download")
        print("=" * 40)
        print()
        
        query = input("Enter search query (e.g., 'V07', 'qwen3tts', 'z-image'): ").strip()
        if not query:
            print("No query provided.")
            return
        
        print("\nWorkflow type:")
        print("1. All workflows")
        print("2. Qwen3-TTS workflows")
        print("3. Z-Image workflows")
        type_choice = input("Select type (1-3, default: 1): ").strip() or "1"
        
        workflow_type = None
        if type_choice == "2":
            workflow_type = "qwen3tts"
        elif type_choice == "3":
            workflow_type = "zimage"
        
        search_and_download(query, workflow_type)
    else:
        workflow_type = args.type if args.type != 'all' else None
        search_and_download(args.query, workflow_type)


if __name__ == '__main__':
    main()

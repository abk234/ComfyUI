#!/usr/bin/env python3
"""
Download ComfyUI workflows from CivitAI, ComfyWorkflows.com, or other sources.

This script helps download workflow JSON files from various sources
and organizes them for use in ComfyUI.

Usage:
    python download_workflow.py <url>
    python download_workflow.py --search "V07"
    python download_workflow.py --url https://civitai.com/models/12345
    python download_workflow.py --url https://comfyworkflows.com/workflow/12345
"""

import os
import sys
import json
import re
import argparse
import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict, Any

# Default workflows directory
WORKFLOWS_DIR = Path(__file__).parent / "workflows" / "downloaded"


def is_comfyworkflows_url(url: str) -> bool:
    """Check if URL is from comfyworkflows.com."""
    return 'comfyworkflows.com' in url.lower()


def extract_workflow_id_from_comfyworkflows(url: str) -> Optional[str]:
    """Extract workflow ID from ComfyWorkflows URL."""
    # Patterns: 
    # - https://comfyworkflows.com/workflow/{id}
    # - https://comfyworkflows.com/workflows/{id}
    match = re.search(r'/workflows?/([^/?]+)', url)
    if match:
        return match.group(1)
    return None


def extract_model_id_from_url(url: str) -> Optional[str]:
    """Extract model ID from CivitAI URL."""
    # Pattern: https://civitai.com/models/{model_id}
    match = re.search(r'/models/(\d+)', url)
    if match:
        return match.group(1)
    return None


def get_civitai_model_info(model_id: str) -> Optional[Dict[str, Any]]:
    """Get model information from CivitAI API."""
    api_url = f"https://civitai.com/api/v1/models/{model_id}"
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching model info: {e}")
        return None


def extract_workflow_from_image(image_path: str) -> Optional[Dict[str, Any]]:
    """Extract workflow JSON from PNG metadata."""
    try:
        from PIL import Image
        from PIL.PngImagePlugin import PngInfo
        
        img = Image.open(image_path)
        if hasattr(img, 'text') and 'workflow' in img.text:
            workflow_json = json.loads(img.text['workflow'])
            return workflow_json
    except Exception as e:
        print(f"Error extracting workflow from image: {e}")
    return None


def download_file(url: str, destination: Path) -> bool:
    """Download a file from URL to destination."""
    try:
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False


def find_workflow_files(model_data: Dict[str, Any]) -> list:
    """Find workflow files (JSON or PNG with embedded workflow) in model data."""
    workflow_files = []
    
    # Check model versions
    for version in model_data.get('modelVersions', []):
        # Check files
        for file in version.get('files', []):
            file_name = file.get('name', '').lower()
            if file_name.endswith('.json') or file_name.endswith('.png'):
                workflow_files.append({
                    'name': file.get('name'),
                    'url': file.get('downloadUrl'),
                    'type': 'json' if file_name.endswith('.json') else 'png',
                    'version': version.get('name', 'unknown')
                })
    
    return workflow_files


def save_workflow(workflow_data: Dict[str, Any], filename: str, model_name: str, workflows_dir: Path = None) -> Path:
    """Save workflow JSON to file."""
    if workflows_dir is None:
        workflows_dir = WORKFLOWS_DIR
    
    # Sanitize filename
    safe_model_name = re.sub(r'[^\w\s-]', '', model_name).strip()
    safe_model_name = re.sub(r'[-\s]+', '-', safe_model_name)
    
    workflow_dir = workflows_dir / safe_model_name
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_path = workflow_dir / filename
    
    with open(workflow_path, 'w', encoding='utf-8') as f:
        json.dump(workflow_data, f, indent=2, ensure_ascii=False)
    
    return workflow_path


def download_workflow_from_comfyworkflows(url: str, workflows_dir: Path = None) -> bool:
    """Download workflow from ComfyWorkflows.com URL."""
    if workflows_dir is None:
        workflows_dir = WORKFLOWS_DIR
    
    workflow_id = extract_workflow_id_from_comfyworkflows(url)
    if not workflow_id:
        # Check if it's a listing page (but not a specific workflow page)
        # Listing pages: /featured, /workflows (without ID), /trending
        # Workflow pages: /workflow/[id] or /workflows/[id]
        is_listing = (
            '/featured' in url or 
            '/trending' in url or 
            url.endswith('/workflows') or
            url.endswith('/workflow') or
            (('/workflows' in url or '/workflow' in url) and not re.search(r'/workflows?/[^/]+', url))
        )
        
        if is_listing:
            print("This is a listing page, not a specific workflow.")
            print("Please provide a direct workflow URL like:")
            print("  https://comfyworkflows.com/workflow/[id]")
            print("  https://comfyworkflows.com/workflows/[id]")
            print("\nTo find workflow URLs:")
            print("1. Visit https://comfyworkflows.com/featured")
            print("2. Click on a workflow to open its page")
            print("3. Copy the URL from your browser")
            print("4. Use that URL with this script")
            return False
        print(f"Could not extract workflow ID from URL: {url}")
        return False
    
    print(f"Fetching workflow from ComfyWorkflows.com (ID: {workflow_id})...")
    
    # Try to fetch the workflow page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        # Handle different status codes
        if response.status_code == 404:
            print(f"Workflow not found (404). The workflow ID '{workflow_id}' may not exist.")
            print("Please verify the URL is correct.")
            return False
        elif response.status_code == 500:
            print(f"Server error (500) when fetching workflow.")
            print("This could mean:")
            print("  - The workflow page requires authentication")
            print("  - The server is temporarily unavailable")
            print("  - The workflow may be private or restricted")
            print("\nTrying alternative approach...")
            # Continue to try extraction anyway
        elif response.status_code != 200:
            print(f"Unexpected status code: {response.status_code}")
            print("Attempting to extract workflow data anyway...")
        
        page_content = response.text
        
        # Try to find workflow JSON in the page
        # Look for JSON in script tags or data attributes
        workflow_data = None
        
        # Pattern 1: Look for JSON in __NEXT_DATA__ or similar (Next.js)
        # Try to find the complete __NEXT_DATA__ block (it can be very large)
        next_data_match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', page_content, re.DOTALL)
        if not next_data_match:
            # Try alternative pattern
            next_data_match = re.search(r'__NEXT_DATA__\s*=\s*({.+?});', page_content, re.DOTALL)
        
        if next_data_match:
            try:
                next_data_str = next_data_match.group(1)
                next_data = json.loads(next_data_str)
                
                # Navigate through the data structure to find workflow
                # Try multiple possible paths
                props = next_data.get('props', {})
                page_props = props.get('pageProps', {})
                
                # Try various possible locations for workflow data
                workflow_data = (
                    page_props.get('workflow') or 
                    page_props.get('data') or
                    page_props.get('workflowData') or
                    page_props.get('workflowJson') or
                    page_props.get('workflow_json') or
                    next_data.get('workflow') or
                    props.get('workflow')
                )
                
                # If we found a dict but it's not the workflow, look deeper
                if workflow_data and isinstance(workflow_data, dict):
                    # Check if it has 'nodes' key (workflow structure)
                    if 'nodes' not in workflow_data:
                        # Maybe the workflow is nested deeper
                        for key in ['workflow', 'data', 'json', 'workflowJson', 'workflow_json']:
                            if key in workflow_data and isinstance(workflow_data[key], dict):
                                if 'nodes' in workflow_data[key]:
                                    workflow_data = workflow_data[key]
                                    break
            except json.JSONDecodeError as e:
                print(f"Could not parse __NEXT_DATA__ JSON: {e}")
            except Exception as e:
                print(f"Error extracting from __NEXT_DATA__: {e}")
        
        # Pattern 2: Look for workflow JSON directly in script tags
        if not workflow_data:
            script_matches = re.findall(r'<script[^>]*>(.*?)</script>', page_content, re.DOTALL)
            for script in script_matches:
                # Look for workflow-like JSON structures
                json_matches = re.findall(r'\{[^{}]*"nodes"[^{}]*\{[^{}]*\}', script)
                for json_str in json_matches:
                    try:
                        potential_workflow = json.loads(json_str)
                        if 'nodes' in potential_workflow:
                            workflow_data = potential_workflow
                            break
                    except:
                        continue
                if workflow_data:
                    break
        
        # Pattern 3: Look for direct JSON download links
        if not workflow_data:
            json_urls = re.findall(r'"(https?://[^"]+\.json)"', page_content)
            for json_url in json_urls:
                try:
                    json_response = requests.get(json_url, headers=headers, timeout=10)
                    if json_response.status_code == 200:
                        workflow_data = json_response.json()
                        if 'nodes' in workflow_data:
                            break
                except:
                    continue
        
        if not workflow_data:
            print("Could not find workflow JSON in the page.")
            print("\nNote: ComfyWorkflows.com uses JavaScript rendering (Next.js/React).")
            print("The workflow data is loaded dynamically after the page loads, so it's not")
            print("available in the initial HTML response.")
            print("\nOptions to download workflows from ComfyWorkflows.com:")
            print("\n1. Use Playwright (recommended for automation):")
            print("   python download_workflow_playwright.py " + url)
            print("   (Install with: pip install playwright && playwright install chromium)")
            print("\n2. Manual download:")
            print(f"   - Open {url} in your browser")
            print("   - Press F12 → Network tab → Reload page")
            print("   - Find API call with JSON containing 'nodes'")
            print("   - Copy JSON and save as .json file")
            print("\n3. Use Chrome extension (see chrome_extension/README.md)")
            print("\n4. Use the ComfyUI extension for uploading:")
            print("   https://github.com/thecooltechguy/ComfyUI-ComfyWorkflows")
            return False
        
        # Save the workflow
        workflow_name = f"workflow_{workflow_id}"
        filename = f"{workflow_name}.json"
        final_path = save_workflow(workflow_data, filename, "comfyworkflows", workflows_dir)
        print(f"\n✓ Successfully downloaded workflow")
        print(f"  Saved to: {final_path}")
        return True
        
    except Exception as e:
        print(f"Error fetching workflow: {e}")
        return False


def download_workflow_from_url(url: str, workflows_dir: Path = None) -> bool:
    """Download workflow from URL (supports CivitAI and ComfyWorkflows.com)."""
    if workflows_dir is None:
        workflows_dir = WORKFLOWS_DIR
    
    # Check if it's a ComfyWorkflows URL
    if is_comfyworkflows_url(url):
        return download_workflow_from_comfyworkflows(url, workflows_dir)
    
    # Otherwise, try CivitAI
    model_id = extract_model_id_from_url(url)
    if not model_id:
        print(f"Unsupported URL format: {url}")
        print("Supported formats:")
        print("  - CivitAI: https://civitai.com/models/12345")
        print("  - ComfyWorkflows: https://comfyworkflows.com/workflow/[id]")
        return False
    
    print(f"Fetching model information for ID: {model_id}")
    model_data = get_civitai_model_info(model_id)
    if not model_data:
        print("Failed to fetch model information")
        return False
    
    model_name = model_data.get('name', f'model_{model_id}')
    print(f"Model: {model_name}")
    
    workflow_files = find_workflow_files(model_data)
    if not workflow_files:
        print("No workflow files found in this model")
        return False
    
    print(f"Found {len(workflow_files)} workflow file(s):")
    for i, wf_file in enumerate(workflow_files, 1):
        print(f"  {i}. {wf_file['name']} ({wf_file['type']}) - Version: {wf_file['version']}")
    
    # Download all workflow files
    downloaded = []
    for wf_file in workflow_files:
        file_url = wf_file['url']
        if not file_url:
            print(f"Skipping {wf_file['name']} - no download URL")
            continue
        
        print(f"\nDownloading {wf_file['name']}...")
        temp_path = workflows_dir / f"temp_{wf_file['name']}"
        
        if download_file(file_url, temp_path):
            if wf_file['type'] == 'json':
                # It's a JSON file, move it to the right location
                with open(temp_path, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                final_path = save_workflow(workflow_data, wf_file['name'], model_name, workflows_dir)
                temp_path.unlink()  # Remove temp file
                downloaded.append(final_path)
                print(f"  ✓ Saved to: {final_path}")
            elif wf_file['type'] == 'png':
                # Try to extract workflow from PNG
                workflow_data = extract_workflow_from_image(str(temp_path))
                if workflow_data:
                    json_filename = wf_file['name'].replace('.png', '.json')
                    final_path = save_workflow(workflow_data, json_filename, model_name, workflows_dir)
                    downloaded.append(final_path)
                    print(f"  ✓ Extracted workflow to: {final_path}")
                else:
                    # Keep the PNG file
                    final_dir = workflows_dir / re.sub(r'[^\w\s-]', '', model_name).strip()
                    final_dir.mkdir(parents=True, exist_ok=True)
                    final_path = final_dir / wf_file['name']
                    temp_path.rename(final_path)
                    downloaded.append(final_path)
                    print(f"  ✓ Saved image to: {final_path}")
        else:
            print(f"  ✗ Failed to download {wf_file['name']}")
    
    if downloaded:
        print(f"\n✓ Successfully downloaded {len(downloaded)} file(s)")
        return True
    else:
        print("\n✗ No files were downloaded")
        return False


def search_civitai_models(query: str, limit: int = 10) -> list:
    """Search for models on CivitAI."""
    api_url = "https://civitai.com/api/v1/models"
    params = {
        'query': query,
        'limit': limit,
        'types': 'Checkpoint,TextualInversion,Hypernetwork,AestheticGradient,LoRA,Controlnet,Poses'
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except Exception as e:
        print(f"Error searching CivitAI: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description='Download ComfyUI workflows from CivitAI or ComfyWorkflows.com'
    )
    parser.add_argument(
        'url',
        nargs='?',
        help='Workflow URL (e.g., https://civitai.com/models/12345 or https://comfyworkflows.com/workflow/12345)'
    )
    parser.add_argument(
        '--search',
        help='Search for models on CivitAI'
    )
    parser.add_argument(
        '--workflows-dir',
        default=None,
        help='Directory to save workflows (default: workflows/downloaded)'
    )
    
    args = parser.parse_args()
    
    # Determine workflows directory
    if args.workflows_dir:
        workflows_dir = Path(args.workflows_dir)
    else:
        workflows_dir = WORKFLOWS_DIR
    
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    if args.search:
        print(f"Searching CivitAI for: {args.search}")
        results = search_civitai_models(args.search)
        
        if not results:
            print("No results found")
            return
        
        print(f"\nFound {len(results)} result(s):\n")
        for i, model in enumerate(results, 1):
            model_id = model.get('id')
            model_name = model.get('name', 'Unknown')
            model_url = f"https://civitai.com/models/{model_id}"
            print(f"{i}. {model_name}")
            print(f"   URL: {model_url}")
            print(f"   Type: {model.get('type', 'Unknown')}")
            print()
        
        choice = input("Enter the number of the model to download (or 'q' to quit): ")
        if choice.lower() == 'q':
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                model_url = f"https://civitai.com/models/{results[idx]['id']}"
                download_workflow_from_url(model_url, workflows_dir)
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")
    
    elif args.url:
        download_workflow_from_url(args.url, workflows_dir)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

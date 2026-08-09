#!/usr/bin/env python3
"""
Download ComfyUI workflows from ComfyWorkflows.com using Playwright.

This script uses Playwright to handle JavaScript-rendered pages and extract
workflow JSON from ComfyWorkflows.com.

Usage:
    python download_workflow_playwright.py https://comfyworkflows.com/workflows/[id]
    python download_workflow_playwright.py --url https://comfyworkflows.com/workflows/[id]
"""

import os
import sys
import json
import re
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

# Default workflows directory
WORKFLOWS_DIR = Path(__file__).parent / "workflows" / "downloaded"


def extract_workflow_id_from_url(url: str) -> Optional[str]:
    """Extract workflow ID from ComfyWorkflows URL."""
    # Patterns: /workflow/{id} or /workflows/{id}
    match = re.search(r'/workflows?/([^/?]+)', url)
    if match:
        return match.group(1)
    return None


def save_workflow(workflow_data: Dict[str, Any], filename: str, workflow_id: str, workflows_dir: Path = None) -> Path:
    """Save workflow JSON to file."""
    if workflows_dir is None:
        workflows_dir = WORKFLOWS_DIR
    
    workflow_dir = workflows_dir / "comfyworkflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_path = workflow_dir / filename
    
    with open(workflow_path, 'w', encoding='utf-8') as f:
        json.dump(workflow_data, f, indent=2, ensure_ascii=False)
    
    return workflow_path


def download_workflow_with_playwright(url: str, workflows_dir: Path = None) -> bool:
    """Download workflow from ComfyWorkflows.com using Playwright."""
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        print("Error: Playwright is not installed.")
        print("Install it with: pip install playwright")
        print("Then run: playwright install chromium")
        return False
    
    if workflows_dir is None:
        workflows_dir = WORKFLOWS_DIR
    
    workflow_id = extract_workflow_id_from_url(url)
    if not workflow_id:
        print(f"Could not extract workflow ID from URL: {url}")
        return False
    
    print(f"Fetching workflow from ComfyWorkflows.com (ID: {workflow_id})...")
    print("Using Playwright to handle JavaScript rendering...")
    
    with sync_playwright() as p:
        # Launch browser
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to the page
            print(f"Loading page: {url}")
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Wait for the page to fully load and be interactive
            print("Waiting for page to load...")
            page.wait_for_timeout(5000)  # Give extra time for JS to execute
            
            # Wait for specific elements that indicate the page is ready
            try:
                # Wait for common elements that appear when workflow is loaded
                page.wait_for_selector('body', timeout=5000)
                # Try to wait for any workflow-related elements
                page.wait_for_timeout(3000)  # Additional wait for async data loading
            except:
                pass  # Continue even if elements don't appear
            
            # Try multiple strategies to get the workflow data
            
            # Strategy 1: Look for workflow data in window object or React state
            print("Attempting to extract workflow data...")
            workflow_data = None
            
            # Try to get workflow from page context
            try:
                # Look for common patterns in the page
                # Check if there's a download button or API call we can intercept
                
                # Strategy 2: Look for API calls that might have the workflow
                print("Checking for API endpoints...")
                
                # Wait for any API calls to complete
                page.wait_for_timeout(2000)
                
                # Try to find workflow data in the page's JavaScript context
                # Many React apps store data in window.__INITIAL_STATE__ or similar
                print("Evaluating JavaScript context for workflow data...")
                workflow_data = page.evaluate("""
                    () => {
                        // Try multiple possible locations for workflow data
                        const possibleLocations = [
                            window.__NEXT_DATA__?.props?.pageProps?.workflow,
                            window.__NEXT_DATA__?.props?.pageProps?.data,
                            window.__NEXT_DATA__?.props?.pageProps?.workflowData,
                            window.__NEXT_DATA__?.props?.pageProps?.workflowJson,
                            window.__INITIAL_STATE__?.workflow,
                            window.workflow,
                            window.__REACT_QUERY_STATE__,
                            document.querySelector('[data-workflow]')?.dataset?.workflow,
                        ];
                        
                        for (const data of possibleLocations) {
                            if (data) {
                                let parsed = data;
                                if (typeof data === 'string') {
                                    try {
                                        parsed = JSON.parse(data);
                                    } catch (e) {
                                        continue;
                                    }
                                }
                                if (parsed && typeof parsed === 'object') {
                                    // Check if it looks like a workflow (has nodes)
                                    if (parsed.nodes && Array.isArray(parsed.nodes)) {
                                        return parsed;
                                    }
                                    // Check nested structures
                                    if (parsed.workflow && parsed.workflow.nodes) {
                                        return parsed.workflow;
                                    }
                                    if (parsed.data && parsed.data.nodes) {
                                        return parsed.data;
                                    }
                                }
                            }
                        }
                        
                        // Try to find any JSON with 'nodes' in the page
                        const scripts = Array.from(document.querySelectorAll('script'));
                        for (const script of scripts) {
                            const content = script.textContent || script.innerHTML;
                            if (content && content.includes('"nodes"')) {
                                try {
                                    // Try to find complete JSON object
                                    const jsonMatch = content.match(/\\{[\\s\\S]{0,50000}"nodes"[\\s\\S]{0,50000}\\}/);
                                    if (jsonMatch) {
                                        const parsed = JSON.parse(jsonMatch[0]);
                                        if (parsed.nodes && Array.isArray(parsed.nodes)) {
                                            return parsed;
                                        }
                                    }
                                } catch (e) {
                                    // Continue searching
                                }
                            }
                        }
                        
                        // Try to access React component state
                        try {
                            const reactRoot = document.querySelector('#__next') || document.body;
                            if (reactRoot && reactRoot._reactInternalInstance) {
                                // This is a long shot, but worth trying
                            }
                        } catch (e) {
                            // React internals not accessible
                        }
                        
                        return null;
                    }
                """)
                
                if workflow_data:
                    print("✓ Found workflow in page JavaScript context")
                else:
                    # Try one more time after waiting longer
                    print("Waiting longer for async data to load...")
                    page.wait_for_timeout(5000)
                    workflow_data = page.evaluate("""
                        () => {
                            // Try again with more time
                            const checkData = (obj, path = '') => {
                                if (!obj || typeof obj !== 'object') return null;
                                if (obj.nodes && Array.isArray(obj.nodes)) return obj;
                                for (const [key, value] of Object.entries(obj)) {
                                    if (typeof value === 'object' && value !== null) {
                                        const result = checkData(value, path + '.' + key);
                                        if (result) return result;
                                    }
                                }
                                return null;
                            };
                            
                            const sources = [
                                window.__NEXT_DATA__,
                                window.__REACT_QUERY_STATE__,
                                window.__APOLLO_STATE__,
                                window.__REDUX_DEVTOOLS_EXTENSION__,
                            ];
                            
                            for (const source of sources) {
                                if (source) {
                                    const found = checkData(source);
                                    if (found) return found;
                                }
                            }
                            return null;
                        }
                    """)
                    if workflow_data:
                        print("✓ Found workflow after extended wait")
                
            except Exception as e:
                print(f"Error extracting from page context: {e}")
            
            # Strategy 3: Try direct API calls first
            if not workflow_data:
                print("Trying direct API endpoints...")
                api_endpoints = [
                    f"https://comfyworkflows.com/api/preview-graph/{workflow_id}",  # Try this first - we know it works
                    f"https://comfyworkflows.com/api/workflows/{workflow_id}",
                    f"https://comfyworkflows.com/api/workflow/{workflow_id}",
                    f"https://comfyworkflows.com/api/v1/workflows/{workflow_id}",
                    f"https://comfyworkflows.com/api/v1/workflow/{workflow_id}",
                ]
                
                # Also try Supabase if we can find the endpoint
                # The Supabase URL might be in the page
                try:
                    supabase_info = page.evaluate("""
                        () => {
                            // Look for Supabase configuration
                            const scripts = Array.from(document.querySelectorAll('script'));
                            for (const script of scripts) {
                                const content = script.textContent || script.innerHTML;
                                if (content && content.includes('supabase')) {
                                    const match = content.match(/https:\\/\\/[^\"']+supabase[^\"']+/);
                                    if (match) return match[0];
                                }
                            }
                            return null;
                        }
                    """)
                    if supabase_info:
                        api_endpoints.append(f"{supabase_info}/rest/v1/workflows?id=eq.{workflow_id}")
                except:
                    pass
                
                for api_url in api_endpoints:
                    try:
                        response = requests.get(api_url, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }, timeout=10)
                        if response.status_code == 200:
                            content_type = response.headers.get('content-type', '').lower()
                            
                            # Try JSON first
                            if 'json' in content_type:
                                try:
                                    data = response.json()
                                    if isinstance(data, dict) and 'nodes' in data:
                                        workflow_data = data
                                        print(f"✓ Found workflow via direct API: {api_url}")
                                        break
                                    # Check nested
                                    for key in ['workflow', 'data', 'workflowJson']:
                                        if key in data and isinstance(data[key], dict) and 'nodes' in data[key]:
                                            workflow_data = data[key]
                                            print(f"✓ Found workflow in nested '{key}' via API: {api_url}")
                                            break
                                    if workflow_data:
                                        break
                                except:
                                    pass
                            
                            # Try HTML (like preview-graph endpoint)
                            if not workflow_data and 'html' in content_type:
                                html_content = response.text
                                if '"nodes"' in html_content:
                                    import re
                                    # Strategy 1: Look for window.workflow = {...}
                                    window_workflow_match = re.search(r'window\.workflow\s*=\s*(\{.*?\});', html_content, re.DOTALL)
                                    if window_workflow_match:
                                        try:
                                            workflow_data = json.loads(window_workflow_match.group(1))
                                            if isinstance(workflow_data, dict) and 'nodes' in workflow_data:
                                                print(f"✓ Found workflow via window.workflow from: {api_url}")
                                                break
                                        except:
                                            pass
                                    
                                    # Strategy 2: Look in script tags
                                    if not workflow_data:
                                        script_matches = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
                                        for script in script_matches:
                                            if '"nodes"' in script:
                                                # Try window.workflow pattern in script
                                                window_match = re.search(r'window\.workflow\s*=\s*(\{.*?\});', script, re.DOTALL)
                                                if window_match:
                                                    try:
                                                        workflow_data = json.loads(window_match.group(1))
                                                        if isinstance(workflow_data, dict) and 'nodes' in workflow_data:
                                                            print(f"✓ Found workflow in script tag from: {api_url}")
                                                            break
                                                    except:
                                                        pass
                                                
                                                # Try to find complete JSON object with nodes
                                                if not workflow_data:
                                                    # Look for { ... "nodes": [...] ... } pattern
                                                    # This is tricky because JSON can be nested, so we need a better approach
                                                    # Try to find the start of a JSON object before "nodes"
                                                    json_start = script.find('"nodes"')
                                                    if json_start > 0:
                                                        # Go backwards to find the opening brace
                                                        brace_pos = script.rfind('{', 0, json_start)
                                                        if brace_pos >= 0:
                                                            # Try to extract from here to a reasonable end
                                                            # Find matching closing brace
                                                            depth = 0
                                                            end_pos = brace_pos
                                                            for i in range(brace_pos, min(brace_pos + 500000, len(script))):
                                                                if script[i] == '{':
                                                                    depth += 1
                                                                elif script[i] == '}':
                                                                    depth -= 1
                                                                    if depth == 0:
                                                                        end_pos = i + 1
                                                                        break
                                                            if end_pos > brace_pos:
                                                                try:
                                                                    json_str = script[brace_pos:end_pos]
                                                                    parsed = json.loads(json_str)
                                                                    if isinstance(parsed, dict) and 'nodes' in parsed:
                                                                        workflow_data = parsed
                                                                        print(f"✓ Found workflow in script JSON from: {api_url}")
                                                                        break
                                                                except:
                                                                    pass
                                                if workflow_data:
                                                    break
                                    
                                    # Also try to find window.__NEXT_DATA__ or similar in HTML
                                    if not workflow_data:
                                        next_data_match = re.search(r'__NEXT_DATA__\s*=\s*({.+?})', html_content, re.DOTALL)
                                        if next_data_match:
                                            try:
                                                next_data = json.loads(next_data_match.group(1))
                                                props = next_data.get('props', {}).get('pageProps', {})
                                                for key in ['workflow', 'data', 'workflowJson', 'workflow_json']:
                                                    if key in props:
                                                        nested = props[key]
                                                        if isinstance(nested, dict) and 'nodes' in nested:
                                                            workflow_data = nested
                                                            print(f"✓ Found workflow in __NEXT_DATA__ from: {api_url}")
                                                            break
                                                        elif isinstance(nested, str):
                                                            try:
                                                                parsed = json.loads(nested)
                                                                if isinstance(parsed, dict) and 'nodes' in parsed:
                                                                    workflow_data = parsed
                                                                    print(f"✓ Found workflow in JSON string from: {api_url}")
                                                                    break
                                                            except:
                                                                pass
                                                if workflow_data:
                                                    break
                                            except:
                                                pass
                                
                                if workflow_data:
                                    break
                    except Exception as e:
                        if 'preview-graph' in api_url:
                            print(f"Error with preview-graph endpoint: {e}")
                        continue
            
            # Strategy 4: Intercept network requests to find API calls
            if not workflow_data:
                print("Intercepting network requests...")
                workflow_data = None
                
                # Get all network responses
                responses = []
                def handle_response(response):
                    try:
                        url = response.url.lower()
                        content_type = response.headers.get('content-type', '').lower()
                        # Look for API endpoints or JSON responses
                        if ('api' in url or 
                            'workflow' in url or 
                            'graph' in url or
                            'preview' in url or
                            content_type.startswith('application/json') or
                            'json' in content_type):
                            responses.append(response)
                    except:
                        pass
                
                # Set up response listener BEFORE navigating
                page.on("response", handle_response)
                
                # Reload to capture all requests
                print("Reloading page to capture API calls...")
                page.reload(wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(8000)  # Give more time for API calls to complete
                
                # Also wait for specific API patterns
                print("Waiting for workflow API calls...")
                try:
                    # Wait for any response that might contain workflow data
                    page.wait_for_response(
                        lambda response: 'workflow' in response.url.lower() or 
                                       'api' in response.url.lower(),
                        timeout=10000
                    )
                    page.wait_for_timeout(2000)  # Give it time to process
                except:
                    pass  # Continue even if timeout
                
                # Check responses for workflow data
                print(f"Checking {len(responses)} API responses...")
                for i, response in enumerate(responses):
                    try:
                        url = response.url
                        status = response.status
                        content_type = response.headers.get('content-type', '').lower()
                        
                        # Log interesting responses
                        if i < 10 or 'workflow' in url.lower() or 'api' in url.lower():
                            print(f"  [{i+1}/{len(responses)}] {status} {url[:100]}...")
                        
                        if status == 200:
                            # Try JSON first
                            if 'json' in content_type or 'application/json' in content_type:
                                try:
                                    data = response.json()
                                    if isinstance(data, dict):
                                        # Check for nodes directly
                                        if 'nodes' in data and isinstance(data['nodes'], (list, dict)):
                                            workflow_data = data
                                            print(f"\n✓ Found workflow in API response!")
                                            print(f"  URL: {url}")
                                            print(f"  Nodes count: {len(data.get('nodes', []))}")
                                            break
                                        # Check nested structures
                                        for key in ['workflow', 'data', 'workflowJson', 'workflow_json', 'workflowData', 'graph', 'prompt']:
                                            if key in data:
                                                nested = data[key]
                                                if isinstance(nested, dict) and 'nodes' in nested:
                                                    workflow_data = nested
                                                    print(f"\n✓ Found workflow in nested '{key}'!")
                                                    print(f"  URL: {url}")
                                                    print(f"  Nodes count: {len(nested.get('nodes', []))}")
                                                    break
                                                elif isinstance(nested, str):
                                                    try:
                                                        parsed = json.loads(nested)
                                                        if isinstance(parsed, dict) and 'nodes' in parsed:
                                                            workflow_data = parsed
                                                            print(f"\n✓ Found workflow in JSON string '{key}'!")
                                                            print(f"  URL: {url}")
                                                            break
                                                    except:
                                                        pass
                                        if workflow_data:
                                            break
                                except Exception as json_error:
                                    # Try to read as text and parse
                                    try:
                                        text = response.text()
                                        if '"nodes"' in text and len(text) > 100:  # Reasonable size
                                            # Try to extract JSON - look for complete objects
                                            # First try to find the main JSON object
                                            try:
                                                # Try parsing the whole text
                                                parsed = json.loads(text)
                                                if isinstance(parsed, dict) and 'nodes' in parsed:
                                                    workflow_data = parsed
                                                    print(f"\n✓ Found workflow in text response!")
                                                    print(f"  URL: {url}")
                                                    break
                                            except:
                                                # Try to find JSON object with nodes
                                                import re
                                                json_match = re.search(r'\{[^{}]*"nodes"[^{}]*\{[^{}]*\}', text, re.DOTALL)
                                                if json_match:
                                                    try:
                                                        workflow_data = json.loads(json_match.group(0))
                                                        if 'nodes' in workflow_data:
                                                            print(f"\n✓ Found workflow in extracted JSON!")
                                                            print(f"  URL: {url}")
                                                            break
                                                    except:
                                                        pass
                                    except Exception as text_error:
                                        continue
                    except Exception as e:
                        if i < 5:  # Only log first few errors
                            print(f"  Error checking response {i}: {e}")
                        continue
            
            # Strategy 5: Try to click download button if it exists
            if not workflow_data:
                print("Looking for download button...")
                try:
                    # Set up download listener before clicking
                    download_promise = page.wait_for_event("download", timeout=10000)
                    
                    # Look for common download button selectors
                    download_selectors = [
                        'button:has-text("Download")',
                        'button:has-text("Export")',
                        'a[download]',
                        '[data-download]',
                        'button[aria-label*="download" i]',
                        'a:has-text("Download")',
                    ]
                    
                    button_clicked = False
                    for selector in download_selectors:
                        try:
                            button = page.query_selector(selector)
                            if button:
                                print(f"Found download button: {selector}")
                                button_clicked = True
                                
                                # Try to get the download URL first
                                download_url = None
                                if button.tag_name.lower() == 'a':
                                    download_url = button.get_attribute('href')
                                else:
                                    download_url = button.get_attribute('data-url') or button.get_attribute('data-href')
                                
                                if download_url:
                                    if not download_url.startswith('http'):
                                        download_url = f"https://comfyworkflows.com{download_url}"
                                    print(f"Downloading from: {download_url}")
                                    try:
                                        response = requests.get(download_url, timeout=30, headers={
                                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                        })
                                        if response.status_code == 200:
                                            workflow_data = response.json()
                                            if 'nodes' in workflow_data:
                                                break
                                    except:
                                        pass
                                
                                # If no direct URL, try clicking and intercepting download
                                if not workflow_data:
                                    try:
                                        button.click()
                                        download = download_promise
                                        # Save the downloaded file temporarily
                                        import tempfile
                                        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
                                            download.save_as(tmp.name)
                                            with open(tmp.name, 'r', encoding='utf-8') as f:
                                                workflow_data = json.load(f)
                                            os.unlink(tmp.name)
                                        if workflow_data and 'nodes' in workflow_data:
                                            print("Successfully downloaded workflow via button click")
                                            break
                                    except Exception as e:
                                        print(f"Error clicking button: {e}")
                        except:
                            continue
                    
                    if not button_clicked:
                        print("No download button found")
                except Exception as e:
                    print(f"Error looking for download button: {e}")
            
            browser.close()
            
            if not workflow_data:
                print("\nCould not extract workflow data automatically.")
                print("The workflow may be private, require authentication, or use a different data structure.")
                print("\nManual download steps:")
                print(f"1. Open {url} in your browser")
                print("2. Press F12 to open DevTools")
                print("3. Go to Network tab")
                print("4. Reload the page")
                print("5. Look for API calls returning JSON")
                print("6. Find the one with 'nodes' in the response")
                print("7. Copy the JSON and save it as a .json file")
                return False
            
            # Validate workflow data
            if not isinstance(workflow_data, dict):
                print("Error: Workflow data is not a valid dictionary")
                return False
            
            if 'nodes' not in workflow_data:
                print("Warning: Workflow data doesn't contain 'nodes' key")
                print("Attempting to save anyway...")
            
            # Save the workflow
            filename = f"workflow_{workflow_id}.json"
            final_path = save_workflow(workflow_data, filename, workflow_id, workflows_dir)
            
            print(f"\n✓ Successfully downloaded workflow")
            print(f"  Saved to: {final_path}")
            return True
            
        except PlaywrightTimeout:
            print("Error: Page load timeout. The page may be taking too long to load.")
            browser.close()
            return False
        except Exception as e:
            print(f"Error: {e}")
            browser.close()
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Download ComfyUI workflows from ComfyWorkflows.com using Playwright'
    )
    parser.add_argument(
        'url',
        nargs='?',
        help='ComfyWorkflows URL (e.g., https://comfyworkflows.com/workflows/[id])'
    )
    parser.add_argument(
        '--url',
        dest='url_flag',
        help='ComfyWorkflows URL (alternative to positional argument)'
    )
    parser.add_argument(
        '--workflows-dir',
        default=None,
        help='Directory to save workflows (default: workflows/downloaded/comfyworkflows)'
    )
    
    args = parser.parse_args()
    
    url = args.url or args.url_flag
    
    if not url:
        parser.print_help()
        return
    
    # Determine workflows directory
    if args.workflows_dir:
        workflows_dir = Path(args.workflows_dir)
    else:
        workflows_dir = WORKFLOWS_DIR
    
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if it's a ComfyWorkflows URL
    if 'comfyworkflows.com' not in url.lower():
        print("Error: This script is for ComfyWorkflows.com URLs only.")
        print("For CivitAI, use: python download_workflow.py")
        return
    
    # Check if it's a listing page
    if '/featured' in url or '/trending' in url or url.endswith('/workflows') or url.endswith('/workflow'):
        print("Error: This is a listing page, not a specific workflow.")
        print("Please provide a direct workflow URL like:")
        print("  https://comfyworkflows.com/workflow/[id]")
        print("  https://comfyworkflows.com/workflows/[id]")
        return
    
    success = download_workflow_with_playwright(url, workflows_dir)
    
    if success:
        print("\n✓ Download complete!")
    else:
        print("\n✗ Download failed. See instructions above for manual download.")


if __name__ == '__main__':
    main()

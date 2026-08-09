#!/usr/bin/env python3
"""
Standalone script to execute install.py scripts from custom nodes.

This script can be called directly to execute an install script for a specific custom node.
It's designed to be used by ComfyUI Manager or other tools that need to execute install scripts.

Usage:
    python utils/execute_install_script.py <custom_node_name>
    python utils/execute_install_script.py <path_to_install.py>
    python utils/execute_install_script.py --node-path /path/to/custom_node
"""

from __future__ import annotations

import sys
import os
import argparse
import logging

# Add parent directory to path so we can import the utility
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.install_custom_node_requirements import execute_install_script, find_and_execute_install_scripts


def main():
    parser = argparse.ArgumentParser(
        description="Execute install.py script from a custom node",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute install script for a specific node by name
  python utils/execute_install_script.py comfyui-rmbg
  
  # Execute install script by providing the path
  python utils/execute_install_script.py custom_nodes/comfyui-rmbg/install.py
  
  # Execute install script by providing the node directory
  python utils/execute_install_script.py --node-path custom_nodes/comfyui-rmbg
        """
    )
    
    parser.add_argument(
        "node_identifier",
        nargs="?",
        help="Custom node name or path to install.py script"
    )
    parser.add_argument(
        "--node-path",
        type=str,
        help="Path to custom node directory"
    )
    parser.add_argument(
        "--custom-nodes-path",
        type=str,
        action="append",
        help="Path to custom_nodes directory (can be specified multiple times)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Execute install scripts for all custom nodes"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    # If --all is specified, execute all install scripts
    if args.all:
        successful, total = find_and_execute_install_scripts(
            custom_nodes_paths=args.custom_nodes_path
        )
        if total > 0:
            print(f"\n✓ Executed install scripts for {successful}/{total} custom node(s)")
            sys.exit(0 if successful == total else 1)
        else:
            print("No install.py scripts found in custom nodes")
            sys.exit(0)
    
    # Determine the install script path
    install_script_path = None
    custom_node_dir = None
    custom_node_name = None
    
    if args.node_path:
        # Use the provided node path
        custom_node_dir = os.path.abspath(args.node_path)
        install_script_path = os.path.join(custom_node_dir, "install.py")
        custom_node_name = os.path.basename(custom_node_dir)
    elif args.node_identifier:
        # Check if it's a direct path to install.py
        if os.path.isfile(args.node_identifier) and args.node_identifier.endswith('.py'):
            install_script_path = os.path.abspath(args.node_identifier)
            custom_node_dir = os.path.dirname(install_script_path)
            custom_node_name = os.path.basename(custom_node_dir)
        elif os.path.isdir(args.node_identifier):
            # It's a directory
            custom_node_dir = os.path.abspath(args.node_identifier)
            install_script_path = os.path.join(custom_node_dir, "install.py")
            custom_node_name = os.path.basename(custom_node_dir)
        else:
            # Assume it's a node name, need to find it
            custom_node_name = args.node_identifier
            
            # Try to find the custom node
            custom_nodes_paths = args.custom_nodes_path
            if custom_nodes_paths is None:
                # Import here to avoid circular dependencies
                try:
                    import folder_paths
                    custom_nodes_paths = folder_paths.get_folder_paths("custom_nodes")
                except ImportError:
                    # Fallback to default path
                    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    custom_nodes_paths = [os.path.join(script_dir, "custom_nodes")]
            
            found = False
            for custom_nodes_path in custom_nodes_paths:
                if not os.path.exists(custom_nodes_path):
                    continue
                
                node_path = os.path.join(custom_nodes_path, custom_node_name)
                if os.path.isdir(node_path):
                    custom_node_dir = node_path
                    install_script_path = os.path.join(node_path, "install.py")
                    found = True
                    break
            
            if not found:
                logging.error(f"Custom node '{custom_node_name}' not found in any custom_nodes directory")
                sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Execute the install script
    success, error_msg = execute_install_script(
        install_script_path,
        custom_node_name=custom_node_name,
        custom_node_dir=custom_node_dir
    )
    
    if success:
        print(f"✓ Successfully executed install script for {custom_node_name}")
        sys.exit(0)
    else:
        print(f"✗ Failed to execute install script for {custom_node_name}")
        if error_msg:
            print(f"Error: {error_msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()

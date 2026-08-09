"""
Utility module for installing requirements.txt files from custom nodes.

This module provides functions to discover and install Python dependencies
from requirements.txt files located in custom node directories.
It tracks which custom nodes have already had their requirements installed
to avoid unnecessary reinstalls.

Also provides utilities for executing install.py scripts from custom nodes.
"""

from __future__ import annotations

import os
import subprocess
import logging
import sys
import json
import hashlib
from pathlib import Path
from typing import List, Tuple, Dict, Optional


def get_state_file_path() -> str:
    """Get the path to the state file that tracks installed requirements."""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    state_dir = os.path.join(script_dir, "user")
    os.makedirs(state_dir, exist_ok=True)
    return os.path.join(state_dir, ".custom_node_requirements_state.json")


def load_installation_state() -> Dict[str, Dict[str, str]]:
    """Load the state of previously installed custom node requirements."""
    state_file = get_state_file_path()
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Failed to load installation state: {e}")
            return {}
    return {}


def save_installation_state(state: Dict[str, Dict[str, str]]) -> None:
    """Save the state of installed custom node requirements."""
    state_file = get_state_file_path()
    try:
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        logging.warning(f"Failed to save installation state: {e}")


def get_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of a file."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except IOError:
        return ""


def is_package_installed(package_spec: str) -> bool:
    """
    Check if a package (from requirements.txt line) is already installed.
    
    Args:
        package_spec: Package specification line from requirements.txt
                     (e.g., "torch>=1.0.0" or "numpy")
    
    Returns:
        True if package appears to be installed, False otherwise
    """
    # Extract package name (handle cases like "package==1.0.0", "package>=1.0", etc.)
    package_name = package_spec.strip().split()[0].split('=')[0].split('[')[0].split(';')[0]
    
    # Skip comments and empty lines
    if not package_name or package_name.startswith('#'):
        return True  # Skip non-package lines
    
    try:
        # Try to import the package to check if it's installed
        # First, normalize the package name (e.g., "pillow" -> "PIL")
        import_map = {
            'pillow': 'PIL',
            'opencv-python': 'cv2',
            'opencv-contrib-python': 'cv2',
        }
        
        import_name = import_map.get(package_name.lower(), package_name)
        
        # Try importing
        __import__(import_name)
        return True
    except ImportError:
        # Package not found, check with pip
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False


def find_custom_node_requirements(custom_nodes_paths: List[str]) -> List[Tuple[str, str]]:
    """
    Find all requirements.txt files in custom node directories.
    
    Args:
        custom_nodes_paths: List of paths to custom_nodes directories
        
    Returns:
        List of tuples (custom_node_name, requirements_file_path)
    """
    requirements_files = []
    
    for custom_nodes_path in custom_nodes_paths:
        if not os.path.exists(custom_nodes_path):
            continue
            
        # Iterate through each custom node directory
        for item in os.listdir(custom_nodes_path):
            item_path = os.path.join(custom_nodes_path, item)
            
            # Skip non-directories and special directories
            if not os.path.isdir(item_path) or item in ["__pycache__", ".git"]:
                continue
                
            # Skip disabled nodes
            if item.endswith(".disabled"):
                continue
                
            # Check for requirements.txt in the custom node directory
            requirements_path = os.path.join(item_path, "requirements.txt")
            if os.path.isfile(requirements_path):
                requirements_files.append((item, requirements_path))
                logging.info(f"Found requirements.txt for custom node: {item}")
    
    return requirements_files


def install_requirements_file(
    requirements_path: str, 
    custom_node_name: str = None,
    force: bool = False,
    check_installed: bool = True
) -> bool:
    """
    Install dependencies from a requirements.txt file.
    
    Args:
        requirements_path: Path to the requirements.txt file
        custom_node_name: Optional name of the custom node (for logging)
        force: If True, reinstall even if already installed
        check_installed: If True, check if packages are already installed before installing
        
    Returns:
        True if installation succeeded, False otherwise
    """
    if not os.path.exists(requirements_path):
        logging.warning(f"Requirements file not found: {requirements_path}")
        return False
    
    node_name = custom_node_name or os.path.basename(os.path.dirname(requirements_path))
    
    # If check_installed is True, verify if all packages are already installed
    if check_installed and not force:
        try:
            with open(requirements_path, 'r') as f:
                requirements_lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            
            all_installed = True
            missing_packages = []
            for line in requirements_lines:
                if line and not is_package_installed(line):
                    all_installed = False
                    # Extract package name for reporting
                    pkg_name = line.split()[0].split('=')[0].split('[')[0].split(';')[0]
                    missing_packages.append(pkg_name)
            
            if all_installed:
                logging.debug(f"All dependencies for {node_name} are already installed, skipping")
                return True
            elif missing_packages:
                logging.info(f"Installing missing dependencies for {node_name}: {', '.join(missing_packages)}")
        except Exception as e:
            logging.debug(f"Could not check installed packages for {node_name}: {e}, proceeding with installation")
    
    try:
        logging.info(f"Installing dependencies for {node_name} from {requirements_path}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_path],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logging.info(f"✓ Successfully installed dependencies for {node_name}")
            return True
        else:
            logging.warning(
                f"⚠ Failed to install some dependencies for {node_name}:\n"
                f"{result.stderr}"
            )
            return False
            
    except Exception as e:
        logging.error(f"✗ Error installing dependencies for {node_name}: {e}")
        return False


def execute_install_script(
    install_script_path: str,
    custom_node_name: str = None,
    custom_node_dir: str = None
) -> Tuple[bool, str]:
    """
    Execute an install.py script from a custom node directory.
    
    This function provides a safe way to execute install scripts with proper
    error handling, logging, and environment setup.
    
    Args:
        install_script_path: Path to the install.py script
        custom_node_name: Optional name of the custom node (for logging)
        custom_node_dir: Optional directory of the custom node (used as working directory)
        
    Returns:
        Tuple of (success: bool, error_message: str)
        If success is True, error_message will be empty.
        If success is False, error_message will contain the error details.
    """
    if not os.path.exists(install_script_path):
        error_msg = f"Install script not found: {install_script_path}"
        logging.error(error_msg)
        return (False, error_msg)
    
    # Validate that it's actually a Python file
    if not install_script_path.endswith('.py'):
        error_msg = f"Install script is not a Python file: {install_script_path}"
        logging.error(error_msg)
        return (False, error_msg)
    
    node_name = custom_node_name or os.path.basename(os.path.dirname(install_script_path))
    
    # Use the custom node directory as working directory if provided, otherwise use script's directory
    working_dir = custom_node_dir or os.path.dirname(install_script_path)
    
    # Ensure the working directory exists
    if not os.path.exists(working_dir):
        error_msg = f"Custom node directory not found: {working_dir}"
        logging.error(error_msg)
        return (False, error_msg)
    
    # Normalize paths to absolute paths
    install_script_path = os.path.abspath(install_script_path)
    working_dir = os.path.abspath(working_dir)
    
    # Check if the script is readable
    if not os.access(install_script_path, os.R_OK):
        error_msg = f"Install script is not readable: {install_script_path}"
        logging.error(error_msg)
        return (False, error_msg)
    
    logging.info(f"Executing install script for {node_name} from {install_script_path}...")
    
    try:
        # Set up environment variables that install scripts might need
        env = os.environ.copy()
        
        # Add the custom node directory and ComfyUI root to PYTHONPATH
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pythonpath_parts = [
            working_dir,
            script_dir,  # ComfyUI root
            env.get('PYTHONPATH', '')
        ]
        env['PYTHONPATH'] = os.pathsep.join([p for p in pythonpath_parts if p]).strip(os.pathsep)
        
        # Ensure we're using the correct Python executable
        python_exe = sys.executable
        if not python_exe:
            error_msg = "Could not determine Python executable"
            logging.error(f"✗ {error_msg}")
            return (False, error_msg)
        
        # Execute the install script using the same Python interpreter
        # Use unbuffered output for better real-time logging
        result = subprocess.run(
            [python_exe, "-u", install_script_path],
            cwd=working_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
            check=False
        )
        
        # Log output regardless of success/failure for debugging
        if result.stdout:
            logging.debug(f"Install script stdout for {node_name}:\n{result.stdout}")
        if result.stderr:
            logging.debug(f"Install script stderr for {node_name}:\n{result.stderr}")
        
        if result.returncode == 0:
            logging.info(f"✓ Successfully executed install script for {node_name}")
            return (True, "")
        else:
            # Combine stderr and stdout for better error reporting
            error_output = ""
            if result.stderr:
                error_output += f"STDERR:\n{result.stderr}\n"
            if result.stdout:
                error_output += f"STDOUT:\n{result.stdout}\n"
            if not error_output:
                error_output = "No output from script"
            
            error_msg = (
                f"Install script failed for {node_name} (exit code {result.returncode})\n"
                f"{error_output}"
            )
            logging.error(f"✗ {error_msg}")
            return (False, error_msg)
            
    except subprocess.TimeoutExpired as e:
        error_msg = f"Install script for {node_name} timed out after 10 minutes"
        logging.error(f"✗ {error_msg}")
        return (False, error_msg)
    except FileNotFoundError as e:
        error_msg = f"Python executable not found: {sys.executable}. Error: {str(e)}"
        logging.error(f"✗ {error_msg}")
        return (False, error_msg)
    except PermissionError as e:
        error_msg = f"Permission denied executing install script for {node_name}: {str(e)}"
        logging.error(f"✗ {error_msg}")
        return (False, error_msg)
    except Exception as e:
        error_msg = f"Unexpected error executing install script for {node_name}: {type(e).__name__}: {str(e)}"
        logging.error(f"✗ {error_msg}")
        import traceback
        logging.debug(f"Traceback: {traceback.format_exc()}")
        return (False, error_msg)


def find_and_execute_install_scripts(
    custom_nodes_paths: List[str] = None,
    custom_node_name: str = None
) -> Tuple[int, int]:
    """
    Find and execute install.py scripts from custom node directories.
    
    Args:
        custom_nodes_paths: Optional list of custom_nodes directory paths.
                          If None, uses default ComfyUI custom_nodes path.
        custom_node_name: Optional specific custom node name to process
        
    Returns:
        Tuple of (successful_executions, total_found)
    """
    if custom_nodes_paths is None:
        # Import here to avoid circular dependencies
        try:
            import folder_paths
            custom_nodes_paths = folder_paths.get_folder_paths("custom_nodes")
        except ImportError:
            # Fallback to default path if folder_paths is not available
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            custom_nodes_paths = [os.path.join(script_dir, "custom_nodes")]
    
    install_scripts = []
    
    for custom_nodes_path in custom_nodes_paths:
        if not os.path.exists(custom_nodes_path):
            continue
            
        # Iterate through each custom node directory
        for item in os.listdir(custom_nodes_path):
            item_path = os.path.join(custom_nodes_path, item)
            
            # Skip non-directories and special directories
            if not os.path.isdir(item_path) or item in ["__pycache__", ".git"]:
                continue
                
            # Skip disabled nodes
            if item.endswith(".disabled"):
                continue
            
            # If a specific node name is provided, only process that one
            if custom_node_name and item != custom_node_name:
                continue
                
            # Check for install.py in the custom node directory
            install_script_path = os.path.join(item_path, "install.py")
            if os.path.isfile(install_script_path):
                install_scripts.append((item, install_script_path, item_path))
                logging.info(f"Found install.py for custom node: {item}")
    
    if not install_scripts:
        logging.info("No install.py scripts found in custom nodes")
        return (0, 0)
    
    logging.info(f"Found {len(install_scripts)} custom node(s) with install.py scripts")
    
    successful = 0
    
    for node_name, install_script_path, node_dir in install_scripts:
        success, error_msg = execute_install_script(
            install_script_path,
            custom_node_name=node_name,
            custom_node_dir=node_dir
        )
        if success:
            successful += 1
        else:
            logging.warning(f"Failed to execute install script for {node_name}: {error_msg}")
    
    return (successful, len(install_scripts))


def install_all_custom_node_requirements(
    custom_nodes_paths: List[str] = None,
    force: bool = False,
    only_new: bool = True
) -> Tuple[int, int]:
    """
    Discover and install requirements.txt files from custom nodes.
    Only installs requirements for new or updated custom nodes by default.
    
    Args:
        custom_nodes_paths: Optional list of custom_nodes directory paths.
                          If None, uses default ComfyUI custom_nodes path.
        force: If True, reinstall all requirements even if already installed
        only_new: If True, only install requirements for new or updated custom nodes
        
    Returns:
        Tuple of (successful_installations, total_found)
    """
    if custom_nodes_paths is None:
        # Import here to avoid circular dependencies
        try:
            import folder_paths
            custom_nodes_paths = folder_paths.get_folder_paths("custom_nodes")
        except ImportError:
            # Fallback to default path if folder_paths is not available
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            custom_nodes_paths = [os.path.join(script_dir, "custom_nodes")]
    
    requirements_files = find_custom_node_requirements(custom_nodes_paths)
    
    if not requirements_files:
        logging.info("No requirements.txt files found in custom nodes")
        return (0, 0)
    
    # Load installation state if we're tracking new nodes only
    state = {}
    if only_new and not force:
        state = load_installation_state()
    
    logging.info(f"Found {len(requirements_files)} custom node(s) with requirements.txt files")
    
    successful = 0
    new_state = {}
    
    for node_name, requirements_path in requirements_files:
        # Check if this node needs installation
        needs_installation = True
        
        if only_new and not force:
            file_hash = get_file_hash(requirements_path)
            node_key = f"{node_name}:{requirements_path}"
            
            # Check if we've already installed this exact version
            if node_key in state:
                stored_hash = state[node_key].get("hash", "")
                if stored_hash == file_hash:
                    logging.debug(f"Skipping {node_name} - requirements already installed (unchanged)")
                    needs_installation = False
                    # Keep the existing state
                    new_state[node_key] = state[node_key]
        
        if needs_installation:
            if install_requirements_file(requirements_path, node_name, force=force, check_installed=not force):
                successful += 1
                # Update state
                file_hash = get_file_hash(requirements_path)
                node_key = f"{node_name}:{requirements_path}"
                new_state[node_key] = {
                    "hash": file_hash,
                    "node_name": node_name,
                    "requirements_path": requirements_path
                }
            else:
                # Keep old state if installation failed
                node_key = f"{node_name}:{requirements_path}"
                if node_key in state:
                    new_state[node_key] = state[node_key]
        else:
            successful += 1  # Count as successful since it's already installed
    
    # Save updated state
    if only_new and not force:
        save_installation_state(new_state)
    
    return (successful, len(requirements_files))


if __name__ == "__main__":
    # Allow running as a script
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Install requirements.txt files and execute install.py scripts from custom nodes"
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
        "--force",
        action="store_true",
        help="Force reinstall all requirements even if already installed"
    )
    parser.add_argument(
        "--install-all",
        action="store_true",
        help="Install all requirements (not just new ones). Default is to only install new/updated requirements."
    )
    parser.add_argument(
        "--execute-install-scripts",
        action="store_true",
        help="Also execute install.py scripts from custom nodes"
    )
    parser.add_argument(
        "--install-script-only",
        action="store_true",
        help="Only execute install.py scripts, skip requirements.txt installation"
    )
    parser.add_argument(
        "--node-name",
        type=str,
        help="Process only a specific custom node by name"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    custom_nodes_paths = args.custom_nodes_path
    if custom_nodes_paths is None:
        custom_nodes_paths = None  # Will use default
    
    exit_code = 0
    
    # Execute install scripts if requested
    if args.execute_install_scripts or args.install_script_only:
        successful, total = find_and_execute_install_scripts(
            custom_nodes_paths,
            custom_node_name=args.node_name
        )
        if total > 0:
            print(f"\n✓ Executed install scripts for {successful}/{total} custom node(s)")
            if successful < total:
                exit_code = 1
        else:
            print("No install.py scripts found in custom nodes")
    
    # Install requirements.txt files unless we're only doing install scripts
    if not args.install_script_only:
        only_new = not args.install_all
        successful, total = install_all_custom_node_requirements(
            custom_nodes_paths, 
            force=args.force,
            only_new=only_new
        )
        
        if total > 0:
            print(f"\n✓ Installed dependencies for {successful}/{total} custom node(s)")
            if successful < total:
                exit_code = 1
        else:
            print("No custom node requirements.txt files found")
    
    sys.exit(exit_code)

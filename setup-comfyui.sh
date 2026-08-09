#!/bin/bash

# ComfyUI Environment Setup Script
# This script sets up the virtual environment and installs dependencies

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/venv"

echo "==================================="
echo "ComfyUI Environment Setup"
echo "==================================="
echo ""

# Prefer Python 3.12 for compatibility with all custom nodes (especially onnxruntime)
PYTHON_CMD=""
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
    echo "✓ Found Python 3.12: $(python3.12 --version)"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$PYTHON_VERSION" = "3.12" ]; then
        PYTHON_CMD="python3"
        echo "✓ Found Python 3.12: $(python3 --version)"
    else
        echo "⚠ Warning: Python 3.12 not found, using $(python3 --version)"
        echo "  Some custom nodes (like ComfyUI-WD14-Tagger) require Python 3.12 for onnxruntime"
        echo "  Consider installing Python 3.12: pyenv install 3.12.8"
        PYTHON_CMD="python3"
    fi
else
    echo "✗ Error: python3 is not installed or not in PATH"
    echo "Please install Python 3.12 (recommended) or Python 3.10+"
    exit 1
fi

# Verify Python version if using python3 (not python3.12)
if [ "$PYTHON_CMD" = "python3" ]; then
    PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.10"
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        echo "✗ Error: Python 3.10 or higher is required (found: $PYTHON_VERSION)"
        exit 1
    fi
fi

echo ""

# Check if virtual environment already exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at: $VENV_DIR"
    echo "Activating virtual environment to verify installation..."
    source "$VENV_DIR/bin/activate"
    
    # Check if requirements are installed
    if python -c "import torch" 2>/dev/null; then
        echo "✓ Virtual environment appears to be set up correctly"
        echo ""
        echo "Checking for new custom node requirements..."
        CUSTOM_NODES_DIR="$SCRIPT_DIR/custom_nodes"
        if [ -d "$CUSTOM_NODES_DIR" ]; then
            python "$SCRIPT_DIR/utils/install_custom_node_requirements.py" --custom-nodes-path "$CUSTOM_NODES_DIR" 2>/dev/null || {
                echo "⚠ Some custom node dependencies may need attention"
            }
        fi
        echo ""
        echo "To start ComfyUI, run: ./start-comfyui.sh"
        echo "To recreate the virtual environment, delete it first: rm -rf $VENV_DIR"
        exit 0
    else
        echo "Virtual environment exists but dependencies may be missing."
        echo "Installing/updating dependencies..."
    fi
fi

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "✗ Failed to create virtual environment"
        exit 1
    fi
    echo "✓ Virtual environment created"
    
    # Verify the venv is using the correct Python version
    VENV_PYTHON_VER=$("$VENV_DIR/bin/python" --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "✓ Virtual environment Python version: $VENV_PYTHON_VER"
    if [ "$VENV_PYTHON_VER" != "3.12" ]; then
        echo "⚠ Warning: Virtual environment is using Python $VENV_PYTHON_VER, not 3.12"
        echo "  Some packages may not be available. Consider recreating with:"
        echo "    rm -rf venv && python3.12 -m venv venv && ./setup-comfyui.sh"
    fi
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Ensure python command is available (create symlink if needed)
if ! command -v python &> /dev/null; then
    echo "Creating python symlink..."
    ln -s python3 "$VENV_DIR/bin/python"
fi

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo ""
    echo "Installing dependencies from requirements.txt..."
    echo "This may take several minutes..."
    python -m pip install -r "$SCRIPT_DIR/requirements.txt"
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "✗ Failed to install some dependencies"
        echo "You may need to install them manually or check for errors above"
        exit 1
    fi
    echo ""
    echo "✓ Dependencies installed successfully"
else
    echo "⚠ Warning: requirements.txt not found, skipping dependency installation"
fi

# Install custom node requirements
echo ""
echo "Checking for custom node requirements.txt files..."
CUSTOM_NODES_DIR="$SCRIPT_DIR/custom_nodes"
if [ -d "$CUSTOM_NODES_DIR" ]; then
    python "$SCRIPT_DIR/utils/install_custom_node_requirements.py" --custom-nodes-path "$CUSTOM_NODES_DIR" || {
        echo "⚠ Warning: Some custom node dependencies may have failed to install"
        echo "You can manually install them later if needed"
    }
    
    # Check for Python 3.14 and onnxruntime compatibility
    PYTHON_VER=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
    if [ "$PYTHON_VER" = "3.14" ] && [ -d "$CUSTOM_NODES_DIR/ComfyUI-WD14-Tagger" ]; then
        python -c "import onnxruntime" 2>/dev/null || {
            echo ""
            echo "⚠ Note: ComfyUI-WD14-Tagger requires onnxruntime, which is not available for Python 3.14 yet"
            echo "  The node is installed but will not work until onnxruntime adds Python 3.14 support"
            echo "  To use this node, recreate the venv with Python 3.12:"
            echo "    rm -rf venv && python3.12 -m venv venv && ./setup-comfyui.sh"
            echo ""
        }
    fi
else
    echo "No custom_nodes directory found, skipping custom node requirements"
fi

# Verify PyTorch installation
echo ""
echo "Verifying PyTorch installation..."
python -c "import torch; print(f'✓ PyTorch version: {torch.__version__}'); print(f'✓ MPS (Metal) available: {torch.backends.mps.is_available()}')" || {
    echo "⚠ Warning: PyTorch verification failed, but installation may still work"
}

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "To start ComfyUI, run: ./start-comfyui.sh"
echo "To stop ComfyUI, run: ./stop-comfyui.sh"
echo ""

#!/bin/bash
# Start ComfyUI (fresh install under workspace_for_ai/eval)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$SCRIPT_DIR/comfyui.pid"
LOG_FILE="$SCRIPT_DIR/comfyui.log"

check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "ComfyUI is already running (PID: $PID)"
            echo "Access: http://127.0.0.1:8188"
            exit 1
        else
            rm -f "$PID_FILE"
        fi
    fi
    if lsof -ti:8188 > /dev/null 2>&1; then
        echo "Warning: Port 8188 is already in use."
        exit 1
    fi
}

echo "==================================="
echo "Starting ComfyUI (eval install)"
echo "==================================="
check_running

# shellcheck disable=SC1091
source "$SCRIPT_DIR/venv/bin/activate"

python -c "import torch; print(f'PyTorch {torch.__version__}; MPS={torch.backends.mps.is_available()}')" || {
    echo "Error: PyTorch not available in venv"
    exit 1
}

cd "$SCRIPT_DIR"
# Bind 0.0.0.0 so Docker (host.docker.internal) can reach ComfyUI from SquadOS
nohup python main.py --listen 0.0.0.0 --port 8188 > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"
sleep 2

if ps -p "$PID" > /dev/null 2>&1; then
    echo "✓ ComfyUI started (PID: $PID)"
    echo "✓ http://127.0.0.1:8188"
    echo "✓ Stop: ./stop-comfyui.sh"
    echo "✓ Logs: tail -f $LOG_FILE"
else
    echo "✗ Failed to start. Check: tail -50 $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi

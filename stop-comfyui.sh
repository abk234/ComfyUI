#!/bin/bash
# Stop ComfyUI (eval install)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$SCRIPT_DIR/comfyui.pid"

kill_process() {
    local pid=$1
    if ps -p "$pid" > /dev/null 2>&1; then
        echo "Stopping ComfyUI (PID: $pid)..."
        kill "$pid"
        for _ in {1..10}; do
            if ! ps -p "$pid" > /dev/null 2>&1; then
                echo "✓ ComfyUI stopped"
                rm -f "$PID_FILE"
                return 0
            fi
            sleep 1
        done
        kill -9 "$pid" 2>/dev/null || true
        sleep 1
        rm -f "$PID_FILE"
        echo "✓ ComfyUI force-stopped"
        return 0
    else
        rm -f "$PID_FILE"
        return 0
    fi
}

if [ -f "$PID_FILE" ]; then
    kill_process "$(cat "$PID_FILE")"
    exit $?
fi

PORT_PIDS=$(lsof -ti:8188 2>/dev/null || true)
if [ -n "$PORT_PIDS" ]; then
    kill_process "$(echo "$PORT_PIDS" | head -1)"
    exit $?
fi

echo "✗ ComfyUI is not running"
exit 1

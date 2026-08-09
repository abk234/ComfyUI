#!/bin/bash
# Status check for ComfyUI (eval install)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$SCRIPT_DIR/comfyui.pid"

echo "==================================="
echo "ComfyUI Status (eval install)"
echo "==================================="

if [ ! -f "$PID_FILE" ]; then
    echo "✗ Not running (no PID file)"
    exit 1
fi

PID=$(cat "$PID_FILE")
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "✗ Stale PID file ($PID)"
    rm -f "$PID_FILE"
    exit 1
fi

echo "✓ Process running (PID: $PID)"

if lsof -ti:8188 > /dev/null 2>&1; then
    echo "✓ Port 8188 listening"
else
    echo "⚠ Port 8188 not listening yet"
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:8188/ 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Web UI reachable (HTTP $HTTP_CODE)"
    exit 0
fi
echo "⚠ Web UI HTTP $HTTP_CODE"
exit 1

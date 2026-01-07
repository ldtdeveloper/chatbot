#!/bin/bash
# Real-time MCP monitoring script
# Monitors backend logs for MCP-related events

echo "=========================================="
echo "🔍 MCP Real-Time Monitor"
echo "=========================================="
echo ""
echo "Monitoring for MCP events..."
echo "Start a widget conversation to see logs"
echo ""
echo "Looking for:"
echo "  ✅ MCP: OAuth token configured"
echo "  ✅ MCP: Authentication headers present"
echo "  🔧 MCP EVENT: mcp_list_tools.*"
echo "  🔧 MCP EVENT: mcp_list_tools.completed"
echo ""
echo "=========================================="
echo ""

# Find uvicorn process
UVICORN_PID=$(ps aux | grep "uvicorn.*main:app" | grep -v grep | awk '{print $2}' | head -1)

if [ -z "$UVICORN_PID" ]; then
    echo "❌ No uvicorn process found"
    exit 1
fi

echo "📡 Monitoring process PID: $UVICORN_PID"
echo ""

# Try to monitor stdout/stderr
if [ -f "/proc/$UVICORN_PID/fd/1" ]; then
    tail -f /proc/$UVICORN_PID/fd/1 2>/dev/null | grep --line-buffered -E "\[Widget WS\].*MCP|mcp_list_tools|MCP EVENT" || {
        echo "Waiting for MCP events..."
        # Fallback: check recent logs
        journalctl -u voice-assistant-backend.service -f 2>/dev/null | grep --line-buffered -E "MCP|mcp" || echo "No MCP events detected yet. Start a conversation to trigger MCP initialization."
    }
else
    echo "⚠️ Cannot access process output directly"
    echo "Checking system logs..."
    journalctl -u voice-assistant-backend.service -f 2>/dev/null | grep --line-buffered -E "MCP|mcp" || echo "Monitoring system logs for MCP events..."
fi


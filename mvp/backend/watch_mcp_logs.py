#!/usr/bin/env python3
"""
Real-time MCP log monitor
Monitors backend output for MCP-related events
"""
import subprocess
import sys
import time
import re

def monitor_mcp_logs():
    """Monitor logs for MCP events"""
    print("=" * 80)
    print("🔍 MCP Real-Time Monitor")
    print("=" * 80)
    print()
    print("Monitoring for MCP events...")
    print("Start a widget conversation to see logs")
    print()
    print("Looking for:")
    print("  ✅ MCP: OAuth token configured")
    print("  ✅ MCP: Authentication headers present")
    print("  🔧 MCP EVENT: mcp_list_tools.in_progress")
    print("  🔧 MCP EVENT: mcp_list_tools.completed")
    print("  ⚠️ MCP EVENT: mcp_list_tools.failed")
    print()
    print("=" * 80)
    print()
    
    # Find uvicorn process
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        
        uvicorn_lines = [line for line in result.stdout.split('\n') 
                        if 'uvicorn' in line and 'main:app' in line and 'grep' not in line]
        
        if not uvicorn_lines:
            print("❌ No uvicorn process found")
            print("   Make sure the backend server is running")
            return
        
        pid = uvicorn_lines[0].split()[1]
        print(f"📡 Monitoring uvicorn process (PID: {pid})")
        print()
        print("Press Ctrl+C to stop monitoring")
        print("-" * 80)
        print()
        
        # Try to read from process output
        # Since uvicorn outputs to stdout, we'll check system logs or provide instructions
        print("💡 To see real-time logs:")
        print("   1. Check the terminal where uvicorn is running")
        print("   2. Or run: journalctl -u voice-assistant-backend.service -f")
        print("   3. Or check the terminal output where you started uvicorn")
        print()
        print("Monitoring for MCP patterns in recent output...")
        print()
        
        # Check if we can access journalctl
        try:
            journal = subprocess.Popen(
                ["journalctl", "-u", "voice-assistant-backend.service", "-f", "--no-pager"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            mcp_patterns = [
                r"MCP",
                r"mcp_list_tools",
                r"mcp.*event",
                r"Authentication headers",
                r"OAuth token"
            ]
            
            print("✅ Monitoring system logs...")
            print()
            
            for line in journal.stdout:
                if any(re.search(pattern, line, re.IGNORECASE) for pattern in mcp_patterns):
                    print(f"📨 {line.strip()}")
                    
        except FileNotFoundError:
            print("⚠️ journalctl not available")
            print("   Please check the terminal where uvicorn is running")
            print("   Or check the process output directly")
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Alternative: Check the terminal where uvicorn is running")
        print("   Look for lines containing 'MCP' or 'mcp'")

if __name__ == "__main__":
    monitor_mcp_logs()


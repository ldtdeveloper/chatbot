import subprocess
import os
import requests  
from app.services.integration_config_service import get_integration_config

MCP_PORT = 8081  # Default for most versions

def start_local_mcp_server(agent_id):
    """
    Start local HubSpot MCP server for the given agent.
    
    Args:
        agent_id: ID of the agent
        
    Returns:
        subprocess.Popen process object
    """
    hubspot_config = get_integration_config(agent_id)
    
    if not hubspot_config or not hubspot_config.get('token'):
        print(f"[MCP Server] No HubSpot token found for agent {agent_id}")
        return None
    
    HUBSPOT_TOKEN = hubspot_config['token']
    
    cmd = [
        "npx", "-y", "@hubspot/mcp-server" 
    ]
    env = os.environ.copy()
    env["HUBSPOT_ACCESS_TOKEN"] = HUBSPOT_TOKEN  

    process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        # Give the server a moment to start
        import time
        time.sleep(2)
        requests.get(f"http://localhost:{MCP_PORT}", timeout=5)
        print(f"[MCP Server] Local HubSpot MCP server started on port {MCP_PORT} for agent {agent_id}")
    except Exception as e:
        print(f"[MCP Server] Server may not be ready yet or failed to start: {e}")
        print("[MCP Server] Check token/scopes and ensure @hubspot/mcp-server is available")
    
    return process
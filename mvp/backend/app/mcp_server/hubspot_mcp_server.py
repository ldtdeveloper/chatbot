import subprocess
import os
import requests  
from app.services.integration_config_service import get_integration_config

MCP_PORT = 8000  # Default for most versions

def start_local_mcp_server(agent_id):
    HUBSPOT_TOKEN = get_integration_config(agent_id)
    cmd = [
        "npx", "-y", "@hubspot/mcp-server" 
    ]
    env = os.environ.copy()
    env["HUBSPOT_ACCESS_TOKEN"] = HUBSPOT_TOKEN  

    process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        requests.get(f"http://localhost:{MCP_PORT}")
        print("Local HubSpot MCP server started on port", MCP_PORT)
    except:
        print("Server failed to start – check token/scopes")
    
    return process
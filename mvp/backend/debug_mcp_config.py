#!/usr/bin/env python3
"""
Debug script to check MCP configuration for an agent
Usage: python debug_mcp_config.py <agent_id>
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.agent import Agent
from app.models.integration_config import IntegrationConfig
from app.services.integration_config_service import get_integration_config

def debug_agent_mcp(agent_id: int):
    db = SessionLocal()
    try:
        # Get agent
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            print(f"❌ Agent {agent_id} not found")
            return
        
        print(f"\n{'='*60}")
        print(f"Agent: {agent.name} (ID: {agent.id})")
        print(f"{'='*60}\n")
        
        # Check MCP server toggle
        print(f"1. MCP Server Toggle:")
        print(f"   enable_mcp_server: {agent.enable_mcp_server}")
        print()
        
        # Check integration config
        print(f"2. Integration Config:")
        config = db.query(IntegrationConfig).filter(
            IntegrationConfig.agent_id == agent_id,
            IntegrationConfig.provider == "hubspot"
        ).first()
        
        if config:
            print(f"   ✅ Config found (ID: {config.id})")
            print(f"   Provider: {config.provider}")
            print(f"   Is Active: {config.is_active}")
            print(f"   Instructions length: {len(config.instructions or '')} chars")
            print(f"   Instructions preview: {(config.instructions or '')[:200]}...")
            print(f"   Has encrypted_key: {bool(config.encrypted_key)}")
        else:
            print(f"   ❌ No integration config found")
        print()
        
        # Check via service
        print(f"3. Service Layer Check:")
        hubspot_config = get_integration_config(agent_id)
        if hubspot_config:
            print(f"   ✅ Config retrieved via service")
            print(f"   Has token: {bool(hubspot_config.get('token'))}")
            if hubspot_config.get('token'):
                token = hubspot_config['token']
                print(f"   Token preview: {token[:10]}...{token[-4:]}")
            print(f"   Has instructions: {bool(hubspot_config.get('instructions'))}")
            if hubspot_config.get('instructions'):
                inst = hubspot_config['instructions']
                print(f"   Instructions preview: {inst[:200]}...")
        else:
            print(f"   ❌ Service returned None")
        print()
        
        # Summary
        print(f"{'='*60}")
        print(f"Summary:")
        if agent.enable_mcp_server and hubspot_config and hubspot_config.get('token'):
            print(f"   ✅ MCP should be enabled and working")
        else:
            print(f"   ❌ MCP may not work:")
            if not agent.enable_mcp_server:
                print(f"      - MCP server toggle is OFF")
            if not hubspot_config:
                print(f"      - No integration config found")
            elif not hubspot_config.get('token'):
                print(f"      - No HubSpot token in config")
        print(f"{'='*60}\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_mcp_config.py <agent_id>")
        print("Example: python debug_mcp_config.py 1")
        sys.exit(1)
    
    try:
        agent_id = int(sys.argv[1])
        debug_agent_mcp(agent_id)
    except ValueError:
        print(f"Error: Agent ID must be a number")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


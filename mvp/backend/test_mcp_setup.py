#!/usr/bin/env python3
"""
Test script to verify MCP setup for an agent
Usage: python3 test_mcp_setup.py <agent_id>
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.agent import Agent
from app.models.integration_config import IntegrationConfig
from app.services.integration_config_service import get_integration_config
from datetime import datetime, timezone

def test_mcp_setup(agent_id: int):
    """Test MCP setup for a specific agent"""
    print("=" * 80)
    print(f"MCP SETUP TEST - Agent ID: {agent_id}")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    try:
        # 1. Check Agent
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            print(f"❌ Agent with ID {agent_id} not found")
            return False
        
        print(f"✅ Agent Found: {agent.name} (ID: {agent.id})")
        print(f"   MCP Server Enabled: {agent.enable_mcp_server}")
        print()
        
        if not agent.enable_mcp_server:
            print("❌ MCP server is DISABLED for this agent")
            print("   Fix: Enable MCP server in agent configuration")
            return False
        
        # 2. Check Integration Config
        config = db.query(IntegrationConfig).filter(
            IntegrationConfig.agent_id == agent_id,
            IntegrationConfig.provider == "hubspot",
            IntegrationConfig.is_active == True
        ).first()
        
        if not config:
            print("❌ No HubSpot integration config found")
            print("   Fix: Create integration config via API or OAuth flow")
            return False
        
        print(f"✅ Integration Config Found (ID: {config.id})")
        print()
        
        # 3. Check Tokens
        has_oauth = bool(config.oauth_access_token)
        has_legacy = bool(config.encrypted_key)
        
        print(f"📋 Token Status:")
        print(f"   OAuth Access Token: {'✅ Present' if has_oauth else '❌ Missing'}")
        print(f"   OAuth Refresh Token: {'✅ Present' if config.oauth_refresh_token else '❌ Missing'}")
        print(f"   OAuth Client ID: {config.oauth_client_id or '❌ Missing'}")
        if config.oauth_token_expires_at:
            if config.oauth_token_expires_at < datetime.now(timezone.utc):
                print(f"   ⚠️ OAuth Token EXPIRED")
            else:
                expires_in = config.oauth_token_expires_at - datetime.now(timezone.utc)
                print(f"   ✅ OAuth Token valid for {expires_in}")
        print(f"   Legacy Encrypted Key: {'✅ Present' if has_legacy else '❌ Missing'}")
        print()
        
        # 4. Test Service Layer
        print(f"📋 Service Layer Test:")
        service_config = get_integration_config(agent_id)
        if not service_config:
            print("   ❌ Service returned None - no valid token available")
            return False
        
        print(f"   ✅ Service returned config")
        print(f"   Has Token: {bool(service_config.get('token'))}")
        print(f"   Is OAuth: {service_config.get('is_oauth', False)}")
        print(f"   Has Instructions: {bool(service_config.get('instructions'))}")
        
        if service_config.get('token'):
            token = service_config['token']
            print(f"   Token Preview: {token[:15]}...{token[-4:]}")
            if service_config.get('is_oauth'):
                print(f"   ✅ OAuth token - should work with HubSpot MCP server")
            else:
                print(f"   ⚠️ Legacy token - may not work with HubSpot MCP server")
        else:
            print(f"   ❌ No token in service response")
            return False
        
        # 5. Simulate MCP Tool Configuration
        print()
        print(f"📋 MCP Tool Configuration (what will be sent to OpenAI):")
        if service_config.get('token'):
            token = service_config['token']
            mcp_tool = {
                "type": "mcp",
                "name": "hubspot",
                "url": "https://mcp.hubspot.com",
                "require_approval": "never",
                "headers": {
                    "Authorization": f"Bearer {token[:15]}...{token[-4:]}"
                }
            }
            import json
            print(json.dumps(mcp_tool, indent=2))
        print()
        
        print("=" * 80)
        print("✅ SETUP TEST: PASSED")
        print("=" * 80)
        print()
        print("Next Steps:")
        print("1. Test the widget connection")
        print("2. Check logs for MCP initialization events:")
        print("   - Look for: '✅ MCP: OAuth token configured'")
        print("   - Look for: '✅ MCP: Authentication headers present'")
        print("   - Look for: '🔧 MCP EVENT: mcp_list_tools.in_progress'")
        print("   - Look for: '🔧 MCP EVENT: mcp_list_tools.completed'")
        print("3. If you see 'mcp_list_tools.failed', check:")
        print("   - Token validity")
        print("   - Field names in MCP tool config")
        print("   - HubSpot MCP server accessibility")
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_mcp_setup.py <agent_id>")
        print("Example: python3 test_mcp_setup.py 1")
        sys.exit(1)
    
    agent_id = int(sys.argv[1])
    success = test_mcp_setup(agent_id)
    sys.exit(0 if success else 1)


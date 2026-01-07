#!/usr/bin/env python3
"""
Get HubSpot OAuth installation URL
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
import urllib.parse

def get_oauth_url(agent_id: int):
    """Generate HubSpot OAuth installation URL"""
    redirect_uri = settings.hubspot_oauth_redirect_uri
    scopes = "crm.objects.contacts.read crm.objects.contacts.write crm.objects.companies.read crm.objects.companies.write"
    
    oauth_url = (
        f"https://app.hubspot.com/oauth/authorize"
        f"?client_id={settings.hubspot_oauth_client_id}"
        f"&scope={urllib.parse.quote(scopes)}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        f"&agent_id={agent_id}"
    )
    
    return oauth_url

if __name__ == "__main__":
    agent_id = 1
    url = get_oauth_url(agent_id)
    print("=" * 80)
    print("HubSpot OAuth Installation URL")
    print("=" * 80)
    print()
    print(f"Agent ID: {agent_id}")
    print()
    print("IMPORTANT: Before using this URL, make sure:")
    print("1. The redirect URI is configured in your HubSpot app:")
    print(f"   {settings.hubspot_oauth_redirect_uri}")
    print()
    print("2. Go to HubSpot App Settings (App ID: 26701588)")
    print("   -> Auth -> Redirect URLs")
    print("   -> Add: http://localhost:8081/api/integration-config/hubspot/oauth/callback")
    print()
    print("=" * 80)
    print("OAuth URL:")
    print("=" * 80)
    print(url)
    print()
    print("=" * 80)
    print("Steps to complete OAuth:")
    print("=" * 80)
    print("1. Copy the URL above")
    print("2. Open it in your browser")
    print("3. Authorize the app in HubSpot")
    print("4. You'll be redirected back with the OAuth token")
    print("5. The token will be automatically saved to the database")
    print("=" * 80)


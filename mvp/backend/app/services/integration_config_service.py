from app.database import SessionLocal
from app.models.integration_config import IntegrationConfig
from app.utils.encryption import decrypt_api_key
from typing import Optional, Dict
from datetime import datetime, timezone, timedelta


def get_integration_config(agent_id: int) -> Optional[Dict[str, str]]:
    """
    Get integration config for an agent (HubSpot token and instructions).
    Prioritizes OAuth tokens over legacy encrypted_key.
    
    Returns:
        Dict with 'token', 'instructions', 'is_oauth' keys, or None if not found
    """
    db = SessionLocal()
    try:
        config = db.query(IntegrationConfig).filter(
                IntegrationConfig.agent_id == agent_id,
                IntegrationConfig.is_active == True
            ).first()
        if not config:
            return None
        
        # Prioritize OAuth tokens over legacy encrypted_key
        token = None
        is_oauth = False
        
        if config.oauth_access_token and config.oauth_client_id:
            # Check if token needs refreshing
            if config.oauth_token_expires_at:
                expires_at = config.oauth_token_expires_at
                if isinstance(expires_at, datetime):
                    # Check if token expires within 5 minutes
                    if datetime.now(timezone.utc) >= expires_at - timedelta(minutes=5):
                        # Try to refresh token
                        refreshed = refresh_hubspot_oauth_token(agent_id, db)
                        if refreshed:
                            # Re-query to get the refreshed token
                            config = db.query(IntegrationConfig).filter(
                                IntegrationConfig.agent_id == agent_id,
                                IntegrationConfig.is_active == True
                            ).first()
                            if not config:
                                # If config was deleted, return None
                                return None
            
            # Use OAuth token (either original or refreshed)
            if config and config.oauth_access_token:
                token = config.oauth_access_token
                is_oauth = True
        
        # Fallback to legacy encrypted_key if no OAuth token
        if not token and config.encrypted_key:
            token = decrypt_api_key(config.encrypted_key)
            is_oauth = False
        
        if not token:
            return None
        
        return {
            'token': token,
            'instructions': config.instructions or '',
            'is_oauth': is_oauth
        }

    finally:
        db.close()


def refresh_hubspot_oauth_token(agent_id: int, db) -> bool:
    """
    Refresh HubSpot OAuth access token using refresh token.
    
    Returns:
        True if refresh was successful, False otherwise
    """
    import requests
    
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.agent_id == agent_id,
        IntegrationConfig.is_active == True
    ).first()
    
    if not config or not config.oauth_refresh_token:
        return False
    
    # Check if client credentials are stored
    if not config.oauth_client_id or not config.oauth_client_secret_encrypted:
        return False
    
    # Decrypt client secret
    client_secret = decrypt_api_key(config.oauth_client_secret_encrypted)
    
    try:
        response = requests.post(
            "https://api.hubapi.com/oauth/v1/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": config.oauth_refresh_token,
                "client_id": config.oauth_client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            config.oauth_access_token = token_data['access_token']
            config.oauth_refresh_token = token_data.get('refresh_token', config.oauth_refresh_token)
            config.oauth_token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_data['expires_in'])
            db.commit()
            return True
        else:
            return False
    except Exception as e:
        print(f"Error refreshing HubSpot OAuth token: {e}")
        return False

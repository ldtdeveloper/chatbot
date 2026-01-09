"""
Third Party Service integration configuration routes (Chatbots)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.integration_config import IntegrationConfig
from app.schemas.integration_config import (
    IntegrationConfigCreate, IntegrationConfigResponse, IntegrationConfigUpdate,IntegrationConfigMasked
)
from app.core.dependencies import get_current_user
from app.utils.encryption import encrypt_api_key, decrypt_api_key
from app.core.config import settings
from datetime import datetime, timezone, timedelta
import requests
import urllib.parse

router = APIRouter(prefix="/api/integration-config", tags=["integration_config"])


@router.post("")
async def create_integration_config(
    config_data: IntegrationConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new integration configuration"""
    config = IntegrationConfig(
        provider=config_data.provider,
        instructions=config_data.instructions,
        is_active=True,
        user_id=current_user.id,
        agent_id = config_data.agent_id
    )
    
    # Handle encrypted_key if provided (legacy)
    if config_data.encrypted_key:
        config.encrypted_key = encrypt_api_key(config_data.encrypted_key)
    elif config_data.oauth_client_id:
        # For OAuth-based integrations (like HubSpot), encrypted_key is not needed
        # But database requires NOT NULL, so set to empty string
        config.encrypted_key = ""
    else:
        # If neither encrypted_key nor OAuth credentials provided, set empty string
        config.encrypted_key = ""
    
    # Handle OAuth client credentials
    if config_data.oauth_client_id:
        config.oauth_client_id = config_data.oauth_client_id
    if config_data.oauth_client_secret:
        config.oauth_client_secret_encrypted = encrypt_api_key(config_data.oauth_client_secret)
    
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return config.id


@router.get("",response_model=List[IntegrationConfigResponse])
async def list_integration_config(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    """List all assistant chatbots for current user"""
    configs = db.query(IntegrationConfig).filter(
        IntegrationConfig.user_id == current_user.id,
        IntegrationConfig.agent_id == agent_id
    ).all()
    for config in configs:
        # Handle legacy encrypted_key
        if config.encrypted_key:
            decrypted_key = decrypt_api_key(config.encrypted_key)
            config.masked_key = decrypted_key[:6]+ "x"* (len(decrypted_key)-9)+decrypted_key[-3:]
        else:
            config.masked_key = None
        
        # Set OAuth status
        config.oauth_connected = bool(config.oauth_access_token and config.oauth_client_id)
        config.oauth_expires_at = config.oauth_token_expires_at

    return configs


@router.get("/{integration_config_id}",response_model =IntegrationConfigResponse)
async def get_integration_config(
    integration_config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific integration config """
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.id == integration_config_id,
        IntegrationConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration Config not found"
        )
    
    # Handle legacy encrypted_key (may be empty for OAuth-based integrations)
    if config.encrypted_key:
        decrypted_key = decrypt_api_key(config.encrypted_key)
        config.masked_key = decrypted_key[:6]+ "x"* (len(decrypted_key)-9)+decrypted_key[-3:]
    else:
        config.masked_key = None

    return config


@router.put("/{integration_config_id}")
async def update_integration_config(
    integration_config_id: int,
    config_data: IntegrationConfigUpdate,
    db: Session = Depends(get_db)
):
    """Update assistant configuration"""
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.id == integration_config_id,
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration config not found"
        )
    
    # Update fields
    update_data = config_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'encrypted_key':
            encrypted_key = encrypt_api_key(value)
            value = encrypted_key
        elif field == 'oauth_client_secret':
            # Encrypt client secret before storing
            config.oauth_client_secret_encrypted = encrypt_api_key(value)
            continue  # Skip setting the field directly
        elif field == 'oauth_client_id':
            config.oauth_client_id = value
            continue  # Already set above

        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    
    return config.id


@router.delete("/{integration_config_id}")
async def delete_integration_config(
    integration_config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete integration config"""
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.id == integration_config_id,
        IntegrationConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration config not found"
        )
    
    db.delete(config)
    db.commit()
    return {"message": "Integration config deleted successfully"}

@router.get("/{integration_config_id}/decrypted-key", response_model= IntegrationConfigMasked)
async def get_decrypted_integration_key(
    integration_config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get decrypted API key for a specific integration config """
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.id == integration_config_id,
        IntegrationConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration Config not found"
        )
    
    # Check if encrypted_key exists (may be empty for OAuth-based integrations)
    if not config.encrypted_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No API key configured for this integration. This integration uses OAuth authentication."
        )
    
    decrypted_key = decrypt_api_key(config.encrypted_key)
    return {"decrypted_key": decrypted_key}


@router.get("/hubspot/oauth/install-url")
async def get_hubspot_oauth_install_url(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get HubSpot OAuth installation URL"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Check if integration config exists for this agent
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.agent_id == agent_id,
        IntegrationConfig.provider == "hubspot",
        IntegrationConfig.user_id == current_user.id
    ).first()
    
    if not config:
        logger.warning(f"[OAuth Install URL] No integration config found for agent {agent_id}, user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="HubSpot integration not configured. Please save your HubSpot Client ID and Client Secret first."
        )
    
    if not config.oauth_client_id:
        logger.warning(f"[OAuth Install URL] No OAuth client ID for agent {agent_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="HubSpot Client ID not configured. Please provide your HubSpot app credentials first."
        )
    
    # Generate OAuth URL using stored client_id
    redirect_uri = settings.hubspot_oauth_redirect_uri
    # Use scopes from settings (can be overridden via env var)
    # IMPORTANT: These scopes MUST match what's configured in your HubSpot app settings
    # Go to HubSpot App Settings -> Auth -> Scopes to see configured scopes
    scopes = getattr(settings, 'hubspot_oauth_scopes', 'crm.objects.contacts.read crm.objects.contacts.write')
    
    # Use 'state' parameter to pass agent_id through OAuth flow
    # HubSpot will return this in the callback, allowing us to identify which agent
    import base64
    import json
    state_data = {"agent_id": agent_id}
    state_encoded = base64.urlsafe_b64encode(json.dumps(state_data).encode()).decode()
    
    oauth_url = (
        f"https://app.hubspot.com/oauth/authorize"
        f"?client_id={config.oauth_client_id}"
        f"&scope={urllib.parse.quote(scopes)}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        f"&state={state_encoded}"
    )
    
    logger.info(f"[OAuth Install URL] Generated OAuth URL for agent {agent_id}, redirect_uri={redirect_uri}")
    
    # Store install URL for reference
    config.oauth_install_url = oauth_url
    db.commit()
    
    return {"install_url": oauth_url, "agent_id": agent_id, "redirect_uri": redirect_uri}


@router.get("/hubspot/oauth/callback")
async def hubspot_oauth_callback(
    code: str = Query(..., description="Authorization code from HubSpot"),
    state: Optional[str] = Query(None, description="State parameter containing agent_id"),
    agent_id: Optional[int] = Query(None, description="Agent ID (legacy, prefer state)"),
    db: Session = Depends(get_db)
):
    """Handle HubSpot OAuth callback and exchange code for tokens"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[OAuth Callback] Received callback with code={code[:20]}..., state={state}, agent_id={agent_id}")
    
    # Determine frontend URL (default to localhost:3000 for local dev)
    # Check CORS origins first, then fallback to API base URL
    frontend_url = "http://localhost:3000"
    if settings.cors_origins and len(settings.cors_origins) > 0:
        # Use first CORS origin as frontend URL
        frontend_url = settings.cors_origins[0]
    elif settings.api_base_url:
        # Try to infer frontend URL from API base URL
        if "localhost" in settings.api_base_url or "127.0.0.1" in settings.api_base_url:
            frontend_url = settings.api_base_url.replace(":8081", ":3000")
        else:
            # For production, frontend might be on same domain
            frontend_url = settings.api_base_url.replace("/api", "").replace(":8081", "")
    
    logger.info(f"[OAuth Callback] Frontend URL: {frontend_url}")
    
    # Extract agent_id from state parameter (preferred) or query parameter (fallback)
    resolved_agent_id = None
    if state:
        try:
            import base64
            import json
            state_decoded = base64.urlsafe_b64decode(state.encode()).decode()
            state_data = json.loads(state_decoded)
            resolved_agent_id = state_data.get("agent_id")
        except Exception as e:
            print(f"[OAuth Callback] Error decoding state parameter: {e}")
    
    # Fallback to query parameter if state decoding failed
    if not resolved_agent_id:
        resolved_agent_id = agent_id
    
    if not resolved_agent_id:
        return RedirectResponse(
            url=f"{frontend_url}/agents?oauth_error=Agent ID not found in callback"
        )
    
    # Find integration config by agent_id and provider
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.agent_id == resolved_agent_id,
        IntegrationConfig.provider == "hubspot"
    ).first()
    
    if not config:
        return RedirectResponse(
            url=f"{frontend_url}/agents?oauth_error=Integration config not found&agent_id={resolved_agent_id}"
        )
    
    # Check if client credentials are stored
    if not config.oauth_client_id or not config.oauth_client_secret_encrypted:
        return RedirectResponse(
            url=f"{frontend_url}/agents?oauth_error=HubSpot app credentials not configured. Please provide Client ID and Client Secret first.&agent_id={resolved_agent_id}"
        )
    
    # Decrypt client secret
    client_secret = decrypt_api_key(config.oauth_client_secret_encrypted)
    
    # Exchange authorization code for tokens
    try:
        response = requests.post(
            "https://api.hubapi.com/oauth/v1/token",
            data={
                "grant_type": "authorization_code",
                "client_id": config.oauth_client_id,
                "client_secret": client_secret,
                "redirect_uri": settings.hubspot_oauth_redirect_uri,
                "code": code
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            error_detail = response.text
            logger.error(f"[OAuth Callback] Token exchange failed: {response.status_code} - {error_detail}")
            # URL encode the error message
            error_encoded = urllib.parse.quote(error_detail[:200])  # Limit error length
            return RedirectResponse(
                url=f"{frontend_url}/agents?oauth_error=Failed to exchange authorization code: {error_encoded}&agent_id={resolved_agent_id}"
            )
        
        token_data = response.json()
        logger.info(f"[OAuth Callback] Token exchange successful for agent {resolved_agent_id}")
        
        # Store OAuth tokens (client_id already stored, don't overwrite)
        config.oauth_access_token = token_data['access_token']
        config.oauth_refresh_token = token_data.get('refresh_token')
        # Keep existing oauth_client_id (don't overwrite with settings)
        expires_in = token_data.get('expires_in', 21600)  # Default 6 hours
        config.oauth_token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        config.oauth_installed_at = datetime.now(timezone.utc)
        config.is_active = True
        
        db.commit()
        logger.info(f"[OAuth Callback] OAuth tokens saved for agent {resolved_agent_id}, expires in {expires_in}s")
        
        # Redirect to frontend with success
        return RedirectResponse(
            url=f"{frontend_url}/agents?oauth_success=true&agent_id={resolved_agent_id}"
        )
        
    except requests.RequestException as e:
        logger.error(f"[OAuth Callback] Request exception: {str(e)}")
        error_msg = urllib.parse.quote(str(e)[:200])
        return RedirectResponse(
            url=f"{frontend_url}/agents?oauth_error=Error exchanging authorization code: {error_msg}&agent_id={resolved_agent_id}"
        )
    except Exception as e:
        logger.error(f"[OAuth Callback] Unexpected error: {str(e)}")
        error_msg = urllib.parse.quote(str(e)[:200])
        return RedirectResponse(
            url=f"{frontend_url}/agents?oauth_error=Unexpected error: {error_msg}&agent_id={resolved_agent_id}"
        )


@router.post("/hubspot/oauth/refresh")
async def refresh_hubspot_oauth_token_endpoint(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually refresh HubSpot OAuth token"""
    from app.services.integration_config_service import refresh_hubspot_oauth_token
    
    # Verify user owns the agent
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.agent_id == agent_id,
        IntegrationConfig.provider == "hubspot",
        IntegrationConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration config not found"
        )
    
    success = refresh_hubspot_oauth_token(agent_id, db)
    
    if success:
        return {"message": "Token refreshed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to refresh token. Check if refresh token exists and credentials are valid."
        )


@router.post("/hubspot/oauth/disconnect")
async def disconnect_hubspot_oauth(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect HubSpot OAuth by clearing OAuth tokens"""
    # Verify user owns the agent
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.agent_id == agent_id,
        IntegrationConfig.provider == "hubspot",
        IntegrationConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration config not found"
        )
    
    # Optionally revoke the token with HubSpot (best practice)
    if config.oauth_access_token and config.oauth_client_id and config.oauth_client_secret_encrypted:
        try:
            import requests
            # Decrypt client secret
            client_secret = decrypt_api_key(config.oauth_client_secret_encrypted)
            # Revoke the access token with HubSpot
            requests.post(
                "https://api.hubapi.com/oauth/v1/token/revoke",
                data={
                    "token": config.oauth_access_token,
                    "client_id": config.oauth_client_id,
                    "client_secret": client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        except Exception as e:
            # Log but don't fail if revocation fails
            print(f"[OAuth Disconnect] Warning: Failed to revoke token with HubSpot: {e}")
    
    # Clear OAuth tokens from database (but keep client credentials)
    config.oauth_access_token = None
    config.oauth_refresh_token = None
    # Keep oauth_client_id and oauth_client_secret_encrypted so user can reconnect
    config.oauth_token_expires_at = None
    config.oauth_installed_at = None
    
    db.commit()
    
    return {"message": "HubSpot OAuth disconnected successfully"}


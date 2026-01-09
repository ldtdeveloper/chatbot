"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IntegrationConfigCreate(BaseModel):
    provider: str
    encrypted_key: Optional[str] = None
    instructions: str
    agent_id : int
    oauth_client_id: Optional[str] = None  # HubSpot app Client ID
    oauth_client_secret: Optional[str] = None  # HubSpot app Client Secret (will be encrypted)

class IntegrationConfigUpdate(BaseModel):
    provider: Optional[str] = None
    encrypted_key: Optional[str] = None
    instructions: Optional[str] = None
    is_active: Optional[bool] = None
    oauth_client_id: Optional[str] = None  # HubSpot app Client ID
    oauth_client_secret: Optional[str] = None  # HubSpot app Client Secret (will be encrypted)

class IntegrationConfigResponse(BaseModel):
    id: int
    provider: str
    instructions: str
    is_active: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    masked_key : Optional[str]
    oauth_connected: Optional[bool] = False  # Whether OAuth is connected
    oauth_expires_at: Optional[datetime] = None  # OAuth token expiration
    oauth_client_id: Optional[str] = None  # HubSpot app Client ID (for display)

    class Config:
        from_attributes = True

class IntegrationConfigMasked(BaseModel):
    masked_key: str
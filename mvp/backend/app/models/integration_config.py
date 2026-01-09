"""
MCP server Configuration model - stores keys and instructions
"""
from sqlalchemy import Column, Integer, String, DateTime, Text,Boolean,ForeignKey,UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class IntegrationConfig(Base):
    __tablename__ = "integration_config"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "agent_id",
            "provider",
            name="uq_user_agent_provider"
        ),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False)  # e.g., "slack", "discord", "hubspot", etc.
    instructions = Column(Text, nullable=False)  # Instructions for MCP server
    encrypted_key = Column(String, nullable=True)  # Encrypted key for MCP server (legacy/fallback)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True) 
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # OAuth fields for HubSpot and other OAuth-based integrations
    oauth_access_token = Column(String, nullable=True)  # OAuth access token
    oauth_refresh_token = Column(String, nullable=True)  # OAuth refresh token
    oauth_client_id = Column(String, nullable=True)  # OAuth app client ID (user-provided)
    oauth_client_secret_encrypted = Column(String, nullable=True)  # Encrypted OAuth app client secret (user-provided)
    oauth_token_expires_at = Column(DateTime(timezone=True), nullable=True)  # Token expiration
    oauth_installed_at = Column(DateTime(timezone=True), nullable=True)  # Installation timestamp
    oauth_install_url = Column(String, nullable=True)  # OAuth installation URL
    
    user = relationship("User", back_populates="integration_config")
    agent = relationship("Agent", back_populates="integration_config")


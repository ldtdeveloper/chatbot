"""
Application configuration with environment support
Supports: LOCAL, DEV, PROD

Set APP_ENV environment variable to switch between environments:
- LOCAL: Local development (default)
- DEV: Development server
- PROD: Production
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from enum import Enum


class Environment(str, Enum):
    LOCAL = "LOCAL"
    DEV = "DEV"
    PROD = "PROD"


def get_env_file():
    """Determine which .env file to load based on APP_ENV"""
    app_env = os.getenv("APP_ENV", "LOCAL").upper()
    
    if app_env == Environment.PROD:
        # Try .env.prod first, then .env
        if os.path.exists(".env.prod"):
            return ".env.prod"
    elif app_env == Environment.DEV:
        # Try .env.dev first, then .env
        if os.path.exists(".env.dev"):
            return ".env.dev"
    
    # Default to .env
    return ".env"


class Settings(BaseSettings):
    # Environment
    app_env: str = os.getenv("APP_ENV", "LOCAL").upper()
    
    # Database
    database_url: str = "sqlite:///./chatbot.db"  # Can be overridden by DATABASE_URL env var
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8081
    debug: bool = True
    
    # CORS - Will be overridden by environment-specific logic
    cors_origins: List[str] = [
        "http://localhost:3000", 
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://localhost",
        "http://127.0.0.1",
        "null"  # Allow file:// protocol (browsers send "null" as origin)
    ]
    
    # OpenAI
    openai_api_base: str = "https://api.openai.com/v1"
    
    # API Base URL for widget code generation
    # This is the public URL where the API is accessible
    # Can be set via API_BASE_URL environment variable
    api_base_url: str = "http://localhost:8081"
    
    # SMTP Email Settings (for weekly reports)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@voiceassistant.ai"
    from_name: str = "Voice Assistant Platform"
    
    # Razorpay Settings
    razorpay_key_id: str = os.getenv("RAZORPAY_KEY_ID","")
    razorpay_key_secret: str = os.getenv("RAZORPAY_KEY_SECRET","")
    
    # HubSpot OAuth Configuration
    hubspot_oauth_redirect_uri: str = "http://localhost:8081/api/integration-config/hubspot/oauth/callback"  # Can be overridden via HUBSPOT_OAUTH_REDIRECT_URI
    hubspot_oauth_scopes: str = "crm.objects.contacts.read crm.objects.contacts.write"

    # Razorpay Payment Gateway (optional)
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""

    # HubSpot OAuth (legacy fields - optional)
    client_id: str = ""
    client_secret_key: str = ""
    oauth_url: str = ""
    redirect_uri: str = ""

    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env that aren't defined here
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Apply environment-specific overrides after loading from .env
        self._apply_environment_config()
    
    def _apply_environment_config(self):
        """Apply environment-specific configuration"""
        env = self.app_env.upper()
        
        if env == Environment.LOCAL:
            # Local development
            self.debug = True
            self.host = "0.0.0.0"
            if not self.cors_origins or self.cors_origins == ["http://localhost:3000", "http://localhost:5173"]:
                self.cors_origins = ["http://localhost:3000", "http://localhost:5173"]
            
        elif env == Environment.DEV:
            # Development server
            self.debug = True
            self.host = "127.0.0.1"
            # CORS should be set in .env file for dev, keep existing if set
            
        elif env == Environment.PROD:
            # Production
            self.debug = False
            self.host = "127.0.0.1"
            # Override CORS for production subdomains
            self.cors_origins = [
                "https://chat.ldttechnology.in",
                "https://chat-api.ldttechnology.in"
            ]
    
    @property
    def is_local(self) -> bool:
        """Check if running in local environment"""
        return self.app_env.upper() == Environment.LOCAL
    
    @property
    def is_dev(self) -> bool:
        """Check if running in dev environment"""
        return self.app_env.upper() == Environment.DEV
    
    @property
    def is_prod(self) -> bool:
        """Check if running in production environment"""
        return self.app_env.upper() == Environment.PROD


settings = Settings()


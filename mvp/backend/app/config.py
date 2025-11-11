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
    database_url: str = "sqlite:///./chatbot.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS - Will be overridden by environment-specific logic
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # OpenAI
    openai_api_base: str = "https://api.openai.com/v1"
    
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        case_sensitive=False
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


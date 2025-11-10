"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.assistant_config import NoiseReductionMode


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: Optional[str] = "default"  # Only superadmin can set role


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# OpenAI Key schemas
class OpenAIKeyCreate(BaseModel):
    key_name: str
    api_key: str


class OpenAIKeyResponse(BaseModel):
    id: int
    key_name: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class OpenAIKeyMaskedResponse(BaseModel):
    masked_key: str


# Agent schemas
class AgentCreate(BaseModel):
    name: str
    domain: str  # TLD domain where widget will be displayed (e.g., example.com)
    openai_key_id: int  # Required API key
    instructions: str  # System instructions for the agent
    voice: Optional[str] = "alloy"  # Voice: Alloy, Ash, Ballad, Cedar, Coral, Echo, Marin, Sage, Shimmer, Verse
    noise_reduction_mode: Optional[str] = "near_field"
    noise_reduction_threshold: Optional[str] = "0.5"
    noise_reduction_prefix_padding_ms: Optional[int] = 300
    noise_reduction_silence_duration_ms: Optional[int] = 500
    agent_config: Optional[dict] = {}  # Additional RealtimeAgent configuration (tools, handoffs, etc.)


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    instructions: Optional[str] = None
    voice: Optional[str] = None
    noise_reduction_mode: Optional[str] = None
    noise_reduction_threshold: Optional[str] = None
    noise_reduction_prefix_padding_ms: Optional[int] = None
    noise_reduction_silence_duration_ms: Optional[int] = None
    agent_config: Optional[dict] = None


class AgentResponse(BaseModel):
    id: int
    name: str
    domain: str
    openai_key_id: int
    instructions: str
    voice: str
    noise_reduction_mode: str
    noise_reduction_threshold: str
    noise_reduction_prefix_padding_ms: int
    noise_reduction_silence_duration_ms: int
    agent_config: dict
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Assistant Config schemas
class AssistantConfigCreate(BaseModel):
    name: str
    agent_id: Optional[int] = None  # Reference to agent configuration
    voice: Optional[str] = "alloy"
    noise_reduction_mode: Optional[NoiseReductionMode] = NoiseReductionMode.NEAR_FIELD
    noise_reduction_threshold: Optional[str] = "0.5"
    noise_reduction_prefix_padding_ms: Optional[int] = 300
    noise_reduction_silence_duration_ms: Optional[int] = 500
    additional_settings: Optional[dict] = {}


class AssistantConfigUpdate(BaseModel):
    name: Optional[str] = None
    agent_id: Optional[int] = None
    voice: Optional[str] = "alloy"
    noise_reduction_mode: Optional[NoiseReductionMode] = NoiseReductionMode.NEAR_FIELD
    noise_reduction_threshold: Optional[str] = "0.5"
    noise_reduction_prefix_padding_ms: Optional[int] = 300
    noise_reduction_silence_duration_ms: Optional[int] = 500
    additional_settings: Optional[dict] = {}


class AssistantConfigResponse(BaseModel):
    id: int
    name: str
    agent_id: Optional[int]  # Reference to agent configuration
    voice: str
    noise_reduction_mode: NoiseReductionMode
    noise_reduction_threshold: str
    noise_reduction_prefix_padding_ms: int
    noise_reduction_silence_duration_ms: int
    additional_settings: dict
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Widget Code Generation
class WidgetCodeResponse(BaseModel):
    widget_code: str
    widget_id: str
    assistant_id: Optional[int] = None
    assistant_name: Optional[str] = None


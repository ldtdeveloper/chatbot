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


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
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


# Prompt schemas
class PromptCreate(BaseModel):
    name: str
    description: Optional[str] = None


class PromptVersionCreate(BaseModel):
    system_instructions: str
    version_number: Optional[int] = None


class PromptVersionResponse(BaseModel):
    id: int
    version_number: int
    system_instructions: str
    openai_version: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PromptResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    openai_prompt_id: Optional[str]
    current_version: int
    created_at: datetime
    versions: List[PromptVersionResponse] = []
    
    class Config:
        from_attributes = True


# Assistant Config schemas
class AssistantConfigUpdate(BaseModel):
    prompt_id: Optional[int] = None
    prompt_version_id: Optional[int] = None
    voice: Optional[str] = "alloy"
    noise_reduction_mode: Optional[NoiseReductionMode] = NoiseReductionMode.NEAR_FIELD
    noise_reduction_threshold: Optional[str] = "0.5"
    noise_reduction_prefix_padding_ms: Optional[int] = 300
    noise_reduction_silence_duration_ms: Optional[int] = 500
    additional_settings: Optional[dict] = {}


class AssistantConfigResponse(BaseModel):
    id: int
    prompt_id: Optional[int]
    prompt_version_id: Optional[int]
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


"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.assistant_config import NoiseReductionMode

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


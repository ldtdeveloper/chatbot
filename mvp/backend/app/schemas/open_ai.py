"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel
from datetime import datetime


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
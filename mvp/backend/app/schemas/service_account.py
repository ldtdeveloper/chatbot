from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ServiceAccountKeyCreate(BaseModel):
    key_name: str  # User-friendly name

class ServiceAccountKeyResponse(BaseModel):
    id: int
    user_id: int
    email: str
    key_name: str
    # Do NOT expose the plain key!
    openai_service_account_id: str  # Real OpenAI ID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True  # Allows from SQLAlchemy model

class ServiceAccountKeyMaskedResponse(BaseModel):
    id: int
    key_name: str
    masked_key: str
    openai_service_account_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
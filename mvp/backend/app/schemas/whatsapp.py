from pydantic import BaseModel, field_validator, model_validator,Field

from typing import Optional
from datetime import datetime


# ─────────────────────────────────────────────
# 1. Create WhatsApp Agent Payload
# (Agent creation only — no OAuth here)
# ─────────────────────────────────────────────
class WhatsappAgentCreatePayload(BaseModel):
    name: str
    instructions: Optional[str] = None
    onboarding_mode: str = "demo"
    startup_message: Optional[str] = None
    phone_number: str = Field(..., description="Real WhatsApp number e.g. 919876543210 (with country code, no +)")  # required
    phone_number_id: Optional[str] = None  # optional, can be filled later

    @model_validator(mode="after")
    def validate_phone(self):
        if not self.phone_number.strip():
            raise ValueError("phone_number is required")
        # Add basic validation if you want
        return self
# ─────────────────────────────────────────────
# 2. Start Embedded Signup (NO TOKEN)
# Frontend calls this → gets redirect_url
# ─────────────────────────────────────────────
class WhatsappConnectRequest(BaseModel):
    text_agent_id: int
    phone_number_id: Optional[str] = None  # optional prefill / trial
    access_token:Optional[str]

    @field_validator("text_agent_id")
    @classmethod
    def text_agent_id_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("text_agent_id must be positive")
        return v


# ─────────────────────────────────────────────
# 3. Connect / Start Response
# ─────────────────────────────────────────────
class WhatsappConnectResponse(BaseModel):
    text_agent_id: int
    status: str
    message: str
    redirect_url: Optional[str] = None
    business_id: Optional[str] = None


# ─────────────────────────────────────────────
# 4. Status Response
# ─────────────────────────────────────────────
class WhatsappConnectionStatus(BaseModel):
    text_agent_id: int
    connected: bool
    status: str
    phone_number_id: Optional[str] = None
    phone_number: Optional[str] = None
    updated_at: Optional[datetime] = None


# ─────────────────────────────────────────────
# 5. WhatsApp Agent Response (Full Details)
# ─────────────────────────────────────────────
class WhatsappAgentResponse(BaseModel):
    id: int
    name: str
    channel: str
    instructions: str
    startup_message: Optional[str] = None
    onboarding_mode: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nested config info
    phone_number: Optional[str] = None
    phone_number_id: Optional[str] = None
    status: Optional[str] = None
    dashboard_slug: Optional[str] = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# 6. WhatsApp Agent Update Payload
# ─────────────────────────────────────────────
class WhatsappAgentUpdatePayload(BaseModel):
    name: Optional[str] = None
    instructions: Optional[str] = None
    startup_message: Optional[str] = None
    onboarding_mode: Optional[str] = None
    phone_number: Optional[str] = None
    phone_number_id: Optional[str] = None
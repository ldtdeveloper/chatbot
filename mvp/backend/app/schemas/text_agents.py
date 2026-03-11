"""
Pydantic schemas for Text-based Agents (WhatsApp + future SMS, Telegram, etc.)
- text_agents: basic agent info (name, channel, instructions)
- whatsapp_configs: WhatsApp-specific credentials & status
"""

from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import datetime


# ─────────────────────────────────────────────
# 1. Create Text Agent Payload (for /agents endpoint)
# ─────────────────────────────────────────────
class TextAgentCreatePayload(BaseModel):
    """
    Used to create a new text-based agent (WhatsApp, SMS, etc.)
    """
    name: str
    channel: str = "whatsapp"  # whatsapp, sms, telegram, etc.
    instructions: Optional[str] = None
    startup_message: Optional[str] = None
    onboarding_mode: str = "demo"  # demo | production

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v: str) -> str:
        v = v.lower()
        if v not in ("whatsapp", "sms", "telegram"):
            raise ValueError("channel must be 'whatsapp', 'sms', or 'telegram' (more can be added later)")
        return v

    @field_validator("onboarding_mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        v = v.lower()
        if v not in ("demo", "production"):
            raise ValueError("onboarding_mode must be 'demo' or 'production'")
        return v


# ─────────────────────────────────────────────
# 2. WhatsApp-Specific Connect Request
# ─────────────────────────────────────────────
class WhatsappConnectRequest(BaseModel):
    """
    Payload for connecting WhatsApp to a text agent
    """
    text_agent_id: int  # ID from text_agents table
    code: Optional[str] = None  # required for production

    @field_validator("text_agent_id")
    @classmethod
    def id_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("text_agent_id must be positive")
        return v


# ─────────────────────────────────────────────
# 3. WhatsApp Connect Response
# ─────────────────────────────────────────────
class WhatsappConnectResponse(BaseModel):
    """
    Response after connect attempt
    """
    text_agent_id: int
    status: str  # demo | connected | pending | error
    message: str
    business_id: Optional[str] = None
    redirect_url: Optional[str] = None


# ─────────────────────────────────────────────
# 4. WhatsApp Connection Status Response
# ─────────────────────────────────────────────
class WhatsappConnectionStatus(BaseModel):
    """
    Status check response for a WhatsApp text agent
    """
    text_agent_id: int
    connected: bool
    status: str
    phone_number_id: Optional[str] = None
    updated_at: Optional[datetime] = None


# ─────────────────────────────────────────────
# 5. Text Agent Response (when fetching agent details)
# ─────────────────────────────────────────────
class TextAgentResponse(BaseModel):
    """
    Basic response when creating or fetching a text agent
    """
    text_agent_id: int
    user_id: int
    channel: str
    name: str
    instructions: Optional[str] = None
    startup_message: Optional[str] = None
    onboarding_mode: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    

    class Config:
        from_attributes = True
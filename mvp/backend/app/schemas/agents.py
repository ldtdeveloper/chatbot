"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
    enable_mcp_server: Optional[bool] = False  # Whether to enable MCP server for this agent
    agent_type: Optional[str] = "WEB"  # Agent type: WEB or PHONE


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
    enable_mcp_server: Optional[bool] = None


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
    enable_mcp_server: Optional[bool]
    is_active: bool
    
    class Config:
        from_attributes = True
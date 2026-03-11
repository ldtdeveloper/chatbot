"""
Agent model for managing Realtime Agent configurations
Based on OpenAI RealtimeAgent: https://openai.github.io/openai-agents-js/openai/agents-realtime/classes/realtimeagent/
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean, Enum, TypeDecorator
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class NoiseReductionMode(str, enum.Enum):
    NEAR_FIELD = "near_field"
    FAR_FIELD = "far_field"


class AgentType(str, enum.Enum):
    WEB = "WEB"
    PHONE = "PHONE"
    WHATSAPP = "WHATSAPP"




class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    openai_key_id = Column(Integer, ForeignKey("service_account_key.id"), nullable=False)  # Required API key - references ServiceAccountKey
    agent_type = Column(ENUM(AgentType, name='agenttype', create_type=False), nullable=False, default=AgentType.WEB)  # Agent type: WEB or PHONE
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)  # TLD domain where widget will be displayed (e.g., example.com)
    
    # Agent configuration (stored locally, used for WebRTC calls)
    instructions = Column(Text, nullable=False)  # System instructions for the agent
    voice = Column(String, default="alloy")  # Voice: Alloy, Ash, Ballad, Cedar, Coral, Echo, Marin, Sage, Shimmer, Verse
    
    # Noise reduction settings (for turn_detection in Realtime API)
    # Using String type and storing enum values directly to avoid PostgreSQL enum name/value mismatch
    noise_reduction_mode = Column(String, default=NoiseReductionMode.NEAR_FIELD.value)
    noise_reduction_threshold = Column(String, default="0.5")  # VAD threshold
    noise_reduction_prefix_padding_ms = Column(Integer, default=300)
    noise_reduction_silence_duration_ms = Column(Integer, default=500)
    
    # Additional RealtimeAgent configuration stored as JSON
    # Can include: tools, handoffs, inputGuardrails, outputGuardrails, etc.
    agent_config = Column(JSON, default={})
    
    # Startup message that bot sends automatically when chat starts
    startup_message = Column(Text, nullable=True)  # Optional startup message (e.g., "Hi, how can I assist you?")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)  # Agent active status - deactivated when wallet balance is zero
    
    user = relationship("User", back_populates="agents")
    assistant_configs = relationship("AssistantConfig", back_populates="agent", cascade="all, delete-orphan")
    integration_config = relationship("IntegrationConfig", back_populates="agent", cascade="all, delete-orphan")
    enable_mcp_server = Column(Boolean, default=False)


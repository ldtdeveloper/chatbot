"""
Agent model for managing Realtime Agent configurations
Based on OpenAI RealtimeAgent: https://openai.github.io/openai-agents-js/openai/agents-realtime/classes/realtimeagent/
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class NoiseReductionMode(str, enum.Enum):
    NEAR_FIELD = "near_field"
    FAR_FIELD = "far_field"


class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    openai_key_id = Column(Integer, ForeignKey("openai_keys.id"), nullable=False)  # Required API key
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)  # TLD domain where widget will be displayed (e.g., example.com)
    
    # Agent configuration (stored locally, used for WebRTC calls)
    instructions = Column(Text, nullable=False)  # System instructions for the agent
    voice = Column(String, default="alloy")  # Voice: Alloy, Ash, Ballad, Cedar, Coral, Echo, Marin, Sage, Shimmer, Verse
    
    # Noise reduction settings (for turn_detection in Realtime API)
    noise_reduction_mode = Column(Enum(NoiseReductionMode), default=NoiseReductionMode.NEAR_FIELD)
    noise_reduction_threshold = Column(String, default="0.5")  # VAD threshold
    noise_reduction_prefix_padding_ms = Column(Integer, default=300)
    noise_reduction_silence_duration_ms = Column(Integer, default=500)
    
    # Additional RealtimeAgent configuration stored as JSON
    # Can include: tools, handoffs, inputGuardrails, outputGuardrails, etc.
    agent_config = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="agents")
    assistant_configs = relationship("AssistantConfig", back_populates="agent", cascade="all, delete-orphan")


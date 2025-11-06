"""
Assistant Configuration model - stores voice, noise reduction, and other settings
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class NoiseReductionMode(str, enum.Enum):
    NEAR_FIELD = "near_field"
    FAR_FIELD = "far_field"


class AssistantConfig(Base):
    __tablename__ = "assistant_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=True)  # Active prompt
    prompt_version_id = Column(Integer, ForeignKey("prompt_versions.id"), nullable=True)  # Active version
    
    # Voice settings (OpenAI Realtime API voice options)
    voice = Column(String, default="alloy")  # alloy, echo, fable, onyx, nova, shimmer
    
    # Noise reduction settings
    noise_reduction_mode = Column(Enum(NoiseReductionMode), default=NoiseReductionMode.NEAR_FIELD)
    noise_reduction_threshold = Column(String, default="0.5")  # VAD threshold
    noise_reduction_prefix_padding_ms = Column(Integer, default=300)
    noise_reduction_silence_duration_ms = Column(Integer, default=500)
    
    # Additional settings stored as JSON
    additional_settings = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="assistant_config")
    prompt = relationship("Prompt")
    prompt_version = relationship("PromptVersion")


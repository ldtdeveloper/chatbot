"""
Interaction model for tracking WebSocket usage and analytics
Tracks each conversation session with OpenAI Realtime API
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    openai_key_id = Column(Integer, ForeignKey("openai_keys.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    
    # Session info
    session_id = Column(String, nullable=False, index=True)  # Unique session identifier
    origin_domain = Column(String, nullable=True)  # Domain where widget was used
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, default=0)  # Duration in seconds
    
    # Usage metrics
    input_tokens = Column(Integer, default=0)  # Estimated input tokens
    output_tokens = Column(Integer, default=0)  # Estimated output tokens
    audio_duration_seconds = Column(Float, default=0)  # Total audio duration
    
    # Cost tracking (estimated based on OpenAI pricing)
    estimated_cost = Column(Float, default=0.0)  # Estimated cost in USD
    
    # Status
    status = Column(String, default="active")  # active, completed, error
    error_message = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", backref="interactions")
    openai_key = relationship("OpenAIKey", backref="interactions")
    agent = relationship("Agent", backref="interactions")


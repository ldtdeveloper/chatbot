"""
Interaction model for tracking WebSocket usage and analytics
Tracks each conversation session with OpenAI Realtime API
Includes REAL token-based cost tracking from OpenAI API responses
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


# OpenAI Realtime API Pricing (gpt-4o-mini-realtime-preview — cheaper tier)
# https://openai.com/api/pricing/
# Note: per-1K token rates for the mini realtime preview model
OPENAI_PRICING = {
    # Audio tokens (gpt-4o-mini-realtime-preview)
    "audio_input_per_1k": 0.01,        # $0.01 per 1K audio input tokens
    "audio_input_cached_per_1k": 0.002, # Cached audio ~80% cheaper
    "audio_output_per_1k": 0.04,       # $0.04 per 1K audio output tokens
    # Text tokens
    "text_input_per_1k": 0.00015,      # $0.15 per 1M -> $0.00015 per 1K
    "text_output_per_1k": 0.0006,      # $0.60 per 1M -> $0.0006 per 1K
}


def calculate_real_cost(
    audio_input_tokens: int = 0,
    audio_output_tokens: int = 0,
    text_input_tokens: int = 0,
    text_output_tokens: int = 0
) -> float:
    """
    Calculate real cost based on OpenAI's token pricing
    
    Returns cost in USD
    """
    cost = 0.0
    
    # Audio costs
    cost += (audio_input_tokens / 1000) * OPENAI_PRICING["audio_input_per_1k"]
    cost += (audio_output_tokens / 1000) * OPENAI_PRICING["audio_output_per_1k"]
    
    # Text costs
    cost += (text_input_tokens / 1000) * OPENAI_PRICING["text_input_per_1k"]
    cost += (text_output_tokens / 1000) * OPENAI_PRICING["text_output_per_1k"]
    
    return round(cost, 6)


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
    
    # ========== DETAILED TOKEN TRACKING ==========
    # Audio tokens (from OpenAI response.done usage)
    audio_input_tokens = Column(Integer, default=0)   # Audio input tokens
    audio_output_tokens = Column(Integer, default=0)  # Audio output tokens
    
    # Text tokens (from OpenAI response.done usage)
    text_input_tokens = Column(Integer, default=0)    # Text input tokens  
    text_output_tokens = Column(Integer, default=0)   # Text output tokens
    
    # Legacy fields (kept for backwards compatibility)
    input_tokens = Column(Integer, default=0)   # Total input tokens (audio + text)
    output_tokens = Column(Integer, default=0)  # Total output tokens (audio + text)
    audio_duration_seconds = Column(Float, default=0)  # Total audio duration
    
    # ========== COST TRACKING ==========
    # Real cost from token counts (calculated using OpenAI pricing)
    estimated_cost = Column(Float, default=0.0)  # Total cost in USD
    
    # Breakdown (for detailed analytics)
    audio_input_cost = Column(Float, default=0.0)   # Cost of audio input
    audio_output_cost = Column(Float, default=0.0)  # Cost of audio output
    text_input_cost = Column(Float, default=0.0)    # Cost of text input
    text_output_cost = Column(Float, default=0.0)   # Cost of text output
    
    # Status
    status = Column(String, default="active")  # active, completed, error
    error_message = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", backref="interactions")
    openai_key = relationship("OpenAIKey", backref="interactions")
    agent = relationship("Agent", backref="interactions")
    
    def update_tokens(
        self,
        audio_input: int = 0,
        audio_output: int = 0,
        text_input: int = 0,
        text_output: int = 0
    ):
        """
        Update token counts and recalculate costs
        Call this when receiving usage data from OpenAI
        """
        # Add to existing counts (accumulate across responses)
        self.audio_input_tokens += audio_input
        self.audio_output_tokens += audio_output
        self.text_input_tokens += text_input
        self.text_output_tokens += text_output
        
        # Update legacy total fields
        self.input_tokens = self.audio_input_tokens + self.text_input_tokens
        self.output_tokens = self.audio_output_tokens + self.text_output_tokens
        
        # Calculate individual costs
        self.audio_input_cost = round((self.audio_input_tokens / 1000) * OPENAI_PRICING["audio_input_per_1k"], 6)
        self.audio_output_cost = round((self.audio_output_tokens / 1000) * OPENAI_PRICING["audio_output_per_1k"], 6)
        self.text_input_cost = round((self.text_input_tokens / 1000) * OPENAI_PRICING["text_input_per_1k"], 6)
        self.text_output_cost = round((self.text_output_tokens / 1000) * OPENAI_PRICING["text_output_per_1k"], 6)
        
        # Calculate total cost
        self.estimated_cost = round(
            self.audio_input_cost + 
            self.audio_output_cost + 
            self.text_input_cost + 
            self.text_output_cost, 
            6
        )
    
    def get_cost_breakdown(self) -> dict:
        """Get detailed cost breakdown"""
        return {
            "tokens": {
                "audio_input": self.audio_input_tokens,
                "audio_output": self.audio_output_tokens,
                "text_input": self.text_input_tokens,
                "text_output": self.text_output_tokens,
                "total_input": self.input_tokens,
                "total_output": self.output_tokens
            },
            "costs": {
                "audio_input": self.audio_input_cost,
                "audio_output": self.audio_output_cost,
                "text_input": self.text_input_cost,
                "text_output": self.text_output_cost,
                "total": self.estimated_cost
            },
            "pricing": OPENAI_PRICING
        }

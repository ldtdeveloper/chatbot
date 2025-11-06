"""
OpenAI API Key model - stores encrypted API keys per user
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class OpenAIKey(Base):
    __tablename__ = "openai_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_name = Column(String, nullable=False)  # User-friendly name for the key
    encrypted_key = Column(String, nullable=False)  # Encrypted API key
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="openai_keys")


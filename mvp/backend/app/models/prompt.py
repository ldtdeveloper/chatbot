"""
Prompt and PromptVersion models for managing Audio Prompts
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Prompt(Base):
    __tablename__ = "prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    openai_prompt_id = Column(String, unique=True, index=True)  # OpenAI's prompt ID
    current_version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="prompts")
    versions = relationship("PromptVersion", back_populates="prompt", cascade="all, delete-orphan")


class PromptVersion(Base):
    __tablename__ = "prompt_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    system_instructions = Column(Text, nullable=False)
    openai_version = Column(String)  # OpenAI's version string (e.g., "8")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    prompt = relationship("Prompt", back_populates="versions")
    
    __table_args__ = (
        {"sqlite_autoincrement": True} if "sqlite" in Base.metadata.bind.url else {}
    )


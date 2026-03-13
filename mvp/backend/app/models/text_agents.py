from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean, Enum, TypeDecorator
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class TextAgent(Base):
    __tablename__ = "text_agents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    openai_key_id = Column(Integer, ForeignKey("service_account_key.id"), nullable=True)

    channel = Column(String(20), nullable=False)  # "whatsapp", "sms", etc.
    name = Column(String(120), nullable=False)
    instructions = Column(Text, nullable=False)
    startup_message = Column(Text, nullable=True)
    onboarding_mode = Column(String(20), default="demo")
    is_active = Column(Boolean, default=True)
    
    whatsapp_config = relationship(
        "WhatsappConfig",
        back_populates="text_agent",
        uselist=False,
        cascade="all, delete-orphan"
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="text_agents")
    conversations = relationship("Conversation", back_populates="text_agent", cascade="all, delete-orphan")
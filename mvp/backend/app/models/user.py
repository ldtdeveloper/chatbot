"""
User model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    SUPERADMIN = "superadmin"
    DEFAULT = "default"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable - set after payment
    role = Column(Enum(UserRole), default=UserRole.DEFAULT, nullable=False)
    is_active = Column(Boolean, default=False)  # Inactive until password is set
    password_set = Column(Boolean, default=False)  # Track if password has been set
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    openai_keys = relationship("OpenAIKey", back_populates="user", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")
    assistant_configs = relationship("AssistantConfig", back_populates="user", cascade="all, delete-orphan")
    integration_config = relationship("IntegrationConfig", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payment_tokens = relationship("PaymentToken", back_populates="user", cascade="all, delete-orphan")


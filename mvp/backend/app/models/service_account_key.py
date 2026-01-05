"""
OpenAI API Key model - stores encrypted API keys per user
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
class ServiceAccountKey(Base):
    __tablename__ = "service_account_key"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    email = Column(String, nullable=False)
    key_name = Column(String, nullable=False)
    # encrypted_key = Column(String, nullable=False),
    service_account_key=Column(String,nullable=False)
    is_active = Column(Boolean, default=True)
    openai_service_account_id = Column(String, nullable=True, index=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="service_account")
"""
Payment Token model for secure payment links
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import secrets


class PaymentToken(Base):
    __tablename__ = "payment_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)  # Secure token for payment link
    plan_type = Column(String, nullable=False)  # starter, pro, enterprise
    amount = Column(Float, nullable=False)  # Amount in USD
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="payment_tokens")
    
    @staticmethod
    def generate_token() -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)


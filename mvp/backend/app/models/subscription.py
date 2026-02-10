"""
Subscription model for tracking user plans and payments
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

class SubscriptionMode(str, enum.Enum):
    PAID = "paid"
    TRIAL = "trial"
    EXPIRED = "expired"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_type = Column(Integer, ForeignKey("plans.id"), nullable=False)
    amount = Column(Float, nullable=False)  # Amount in USD
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    subscription_mode = Column(String, nullable = False, default = "paid")
    # Razorpay details
    razorpay_order_id = Column(String, nullable=True, index=True)
    razorpay_payment_id = Column(String, nullable=True)
    razorpay_signature = Column(String, nullable=True)
    
    # Subscription dates
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="subscriptions")
    plans = relationship("Plans",back_populates ="subscriptions")



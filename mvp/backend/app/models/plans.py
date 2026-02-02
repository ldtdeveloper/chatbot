"""
Plan model for plan management by superadmin
"""
from sqlalchemy import Column, Integer, String,Float, Text, DateTime, Boolean,JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.orm import relationship
import enum

class Currency(str, enum.Enum):
    USD = "USD"  # US Dollar
    INR = "INR"  # Indian Rupee
    BHD = "BHD"  # Bahraini Dinar
    KWD = "KWD"  # Kuwaiti Dinar
    OMR = "OMR"  # Omani Rial
    SAR = "SAR"  # Saudi Riyal
    AED = "AED"  # UAE Dirham
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound

class PlanType(str, enum.Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class Plans(Base):
    '''Plans for subscription'''
    __tablename__ = 'plans'

    id = Column(Integer,primary_key = True, index = True)
    name = Column(String,nullable = False)
    description = Column(Text, nullable = True)
    
    # Currency for the plan
    currency = Column(String, nullable=False, default="USD")  # USD, INR, BHD, etc.
    
    # Wallet credits user gets when purchasing this plan
    wallet_credits = Column(Integer, nullable = False, default=0)
    
    # Plan type: monthly or yearly
    plan_type = Column(String, nullable = False, default="monthly")  # monthly, yearly

    # Price of plan
    price = Column(Float, nullable = False)
    
    # Features in plan 
    features = Column(JSON, nullable = False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    #Only active plans can be used by user
    is_active = Column(Boolean,default = True)
    
    #Relationshps
    subscriptions = relationship("Subscription", back_populates="plans", cascade="all, delete-orphan")
    payment_tokens = relationship("PaymentToken", back_populates="plan", cascade="all, delete-orphan")
"""
Plan model for plan management by superadmin
"""
from sqlalchemy import Column, Integer, String,Float, Text, DateTime, Boolean,JSON
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.orm import relationship

class Plans(Base):
    '''Plans for subscription'''
    __tablename__ = 'plans'

    id = Column(Integer,primary_key = True, index = True)
    name = Column(String,nullable = False)
    code = Column(String, nullable = False)
    description = Column(Text, nullable = True)

    # Credits for user 
    credits = Column(Integer, nullable = False)

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
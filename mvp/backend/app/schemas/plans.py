"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime

class PlanCreate(BaseModel):
    name: str
    description: Optional[str] = None
    currency: str = "USD"  # USD, INR, BHD, etc.
    wallet_credits: int
    plan_type: str = "monthly"  # monthly, yearly
    price: float
    features: List[str]

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[str] = None
    wallet_credits: Optional[int] = None
    plan_type: Optional[str] = None
    is_active: Optional[bool] = None
    price: Optional[float] = None
    features: Optional[List[str]] = None

class PlanResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    currency: str
    wallet_credits: int
    plan_type: str
    is_active: bool
    price: float
    created_at: datetime
    updated_at: Optional[datetime]
    features: List[str]
    
    class Config:
        from_attributes = True
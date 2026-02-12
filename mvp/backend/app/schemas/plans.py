"""
Pydantic schemas for API requests and responses
"""
from click import INT
from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime

from sqlalchemy import Integer

class PlanCreate(BaseModel):
    name: str
    description: Optional[str] = None
    currency: str = "USD"  # USD, INR, BHD, etc.
    # wallet_credits: int
    plan_type: str = "monthly"  # monthly, yearly
    price: float
    minutes: int  
    number_of_agents: Optional[int] = None
    features: List[str]
    is_trial: Optional[bool] = None
    number_of_agents: int

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[str] = None
    wallet_credits: Optional[int] = None
    plan_type: Optional[str] = None
    is_active: Optional[bool] = None
    minutes:Optional[int]=None
    price: Optional[float] = None
    features: Optional[List[str]] = None
    minutes : Optional[int] = None
    number_of_agents : Optional[int] = None

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
    minutes:Optional[int]=None
    features: List[str]
    is_trial: bool
    number_of_agents : int
    minutes : int
    
    class Config:
        from_attributes = True
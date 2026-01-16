"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime

class PlanCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    credits: int
    price: float
    features: List[str]

class PlanUpdate(BaseModel):
    name: Optional[str]= None
    code: Optional[str]= None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    credits: Optional[int] = None
    price: Optional[float] = None
    features: Optional[List[str]] = None

class PlanResponse(BaseModel):
    id: int
    name: str
    code : str
    description : str
    is_active: bool
    credits: int
    price : float
    created_at: datetime
    updated_at: Optional[datetime]
    features : List[str]
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
class ActiveSubscription(BaseModel):
    id: int
    subscription_mode: str
    is_active: bool
    start_date: datetime
    end_date: Optional[datetime] = None
    plan_name: Optional[str] = None
    plan_id: Optional[int] = None

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: Optional[str] = None  # Optional - not required for initial registration
    role: Optional[str] = "default"  # Only superadmin can set role

class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str
    plan_id: int 

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None  # Only superadmin can set the role


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    created_at: datetime
    wallet_balance: Optional[float] = None  # Only for non-superadmin users
    remaining_minutes: int 
    subscription_mode: Optional[str] = None
    allowed_agents : int
    
    class Config:
        from_attributes = True
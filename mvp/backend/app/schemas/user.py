from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

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
    
    class Config:
        from_attributes = True
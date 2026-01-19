from pydantic import BaseModel,EmailStr,field_validator
from typing import Optional

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    low_balance: Optional[bool] = False
    wallet_balance: Optional[float] = None

class SetupPasswordRequest(BaseModel):
    token: str  # Payment token
    password: str

class ChangePassword(BaseModel):
    old_password : str
    new_password : str
    confirm_password : str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, confirm_password, info):
        password = info.data.get("password")
        if password and confirm_password != password:
            raise ValueError("Passwords do not match")
        return confirm_password
    
class ResetPassword(BaseModel):
    new_password : str
    
class ForgetPasswordRequest(BaseModel):
    email : str

#Prefetch details of user
class PreFetchDetails(BaseModel):
    email : str
    plan : Optional [str] = None

class ChangeEmail(BaseModel):
    email : str

class AddToWalletRequest(BaseModel):
    amount: float
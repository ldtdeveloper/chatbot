"""
Dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status
from typing import Optional
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.subscription import Subscription, PaymentStatus
from app.utils.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    # Convert string back to int (JWT sub is stored as string)
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def require_active_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency that requires user to have an active paid subscription.
    Superadmins are exempt from this requirement.
    """
    # Check if user is superadmin - exempt from subscription requirement
    is_superadmin = False
    if hasattr(current_user.role, 'value'):
        is_superadmin = current_user.role.value == UserRole.SUPERADMIN.value
    else:
        is_superadmin = str(current_user.role) == str(UserRole.SUPERADMIN.value) or current_user.role == UserRole.SUPERADMIN
    
    if is_superadmin:
        return current_user
    
    # Check for active subscription
    now = datetime.now(timezone.utc)
    active_subscription = db.query(Subscription).filter(
        and_(
            Subscription.user_id == current_user.id,
            Subscription.payment_status == PaymentStatus.SUCCESS,
            Subscription.is_active == True,
            Subscription.end_date >= now
        )
    ).first()
    
    if not active_subscription:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Active subscription required. Please complete payment to access the platform."
        )
    
    return current_user

def get_optional_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Optional auth: returns User if token valid, else None
    """
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None


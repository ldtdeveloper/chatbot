"""
Role-based access control utilities
"""
from fastapi import HTTPException, status
from app.models.user import User, UserRole


def require_superadmin(current_user: User) -> User:
    """Require the current user to be a superadmin"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )
    return current_user


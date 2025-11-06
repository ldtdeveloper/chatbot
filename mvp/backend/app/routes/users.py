"""
User management routes (superadmin only)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas import UserCreate, UserResponse
from app.dependencies import get_current_user
from app.utils.auth import get_password_hash
from app.utils.roles import require_superadmin

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user (superadmin only)"""
    require_superadmin(current_user)
    
    # Check if user already exists
    db_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Validate role
    role = UserRole.DEFAULT
    if user_data.role:
        try:
            role = UserRole(user_data.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {[r.value for r in UserRole]}"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get("", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all users (superadmin only)"""
    require_superadmin(current_user)
    
    users = db.query(User).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific user (superadmin only)"""
    require_superadmin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.patch("/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle user active status (superadmin only)"""
    require_superadmin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deactivating yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/{user_id}/profile")
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile with all their data (superadmin only)"""
    require_superadmin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    from app.models.agent import Agent
    from app.models.assistant_config import AssistantConfig
    from app.models.openai_key import OpenAIKey
    
    # Get user's agents, assistants, and keys
    agents = db.query(Agent).filter(Agent.user_id == user_id).all()
    assistants = db.query(AssistantConfig).filter(AssistantConfig.user_id == user_id).all()
    keys = db.query(OpenAIKey).filter(OpenAIKey.user_id == user_id).all()
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at
        },
        "agents": [{"id": a.id, "name": a.name, "description": a.description} for a in agents],
        "assistants": [{"id": a.id, "name": a.name, "voice": a.voice, "created_at": a.created_at} for a in assistants],
        "api_keys_count": len(keys),
        "active_keys_count": len([k for k in keys if k.is_active])
    }


@router.get("/{user_id}/widgets")
async def get_user_widgets(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all widget codes created by a user (superadmin only)"""
    require_superadmin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    from app.models.assistant_config import AssistantConfig
    from app.models.openai_key import OpenAIKey
    
    assistants = db.query(AssistantConfig).filter(AssistantConfig.user_id == user_id).all()
    
    # Generate widget codes for each assistant
    widgets = []
    for assistant in assistants:
        try:
            # Check if user has active OpenAI key
            active_key = db.query(OpenAIKey).filter(
                OpenAIKey.user_id == user_id,
                OpenAIKey.is_active == True
            ).first()
            
            if not active_key:
                widgets.append({
                    "assistant_id": assistant.id,
                    "assistant_name": assistant.name,
                    "error": "No active OpenAI API key found"
                })
                continue
            
            # Generate widget code manually (can't call route directly)
            import uuid
            widget_id = str(uuid.uuid4())
            widget_code = f"""
<!-- Voice Assistant Widget: {assistant.name} -->
<script>
(function() {{
    const widgetId = '{widget_id}';
    const assistantId = {assistant.id};
    const apiBaseUrl = window.location.protocol + '//' + window.location.host;
    
    console.log('Voice Assistant Widget Loaded:', widgetId, 'for Assistant:', assistantId);
    
    // TODO: Implement widget initialization
    // - Create widget UI
    // - Connect to backend WebSocket proxy
    // - Handle audio input/output
    // - Display transcriptions
}})();
</script>
"""
            widgets.append({
                "assistant_id": assistant.id,
                "assistant_name": assistant.name,
                "widget_id": widget_id,
                "widget_code": widget_code.strip()
            })
        except Exception as e:
            widgets.append({
                "assistant_id": assistant.id,
                "assistant_name": assistant.name,
                "error": str(e)
            })
    
    return {
        "user_id": user_id,
        "username": user.username,
        "widgets": widgets
    }


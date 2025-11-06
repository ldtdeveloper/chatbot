"""
Assistant configuration routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.assistant_config import AssistantConfig
from app.schemas import AssistantConfigUpdate, AssistantConfigResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/assistant-config", tags=["assistant-config"])


@router.get("", response_model=AssistantConfigResponse)
async def get_assistant_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assistant configuration for current user"""
    config = db.query(AssistantConfig).filter(
        AssistantConfig.user_id == current_user.id
    ).first()
    
    if not config:
        # Create default config if it doesn't exist
        config = AssistantConfig(user_id=current_user.id)
        db.add(config)
        db.commit()
        db.refresh(config)
    
    return config


@router.put("", response_model=AssistantConfigResponse)
async def update_assistant_config(
    config_data: AssistantConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update assistant configuration"""
    config = db.query(AssistantConfig).filter(
        AssistantConfig.user_id == current_user.id
    ).first()
    
    if not config:
        config = AssistantConfig(user_id=current_user.id)
        db.add(config)
    
    # Update fields
    update_data = config_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    
    return config


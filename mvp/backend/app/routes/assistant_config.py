"""
Assistant configuration routes (Chatbots)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.assistant_config import AssistantConfig
from app.schemas import (
    AssistantConfigCreate, AssistantConfigUpdate, AssistantConfigResponse
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/assistants", tags=["assistants"])


@router.post("", response_model=AssistantConfigResponse)
async def create_assistant(
    config_data: AssistantConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new assistant chatbot"""
    config = AssistantConfig(
        user_id=current_user.id,
        name=config_data.name,
        agent_id=config_data.agent_id,
        voice=config_data.voice or "alloy",
        noise_reduction_mode=config_data.noise_reduction_mode,
        noise_reduction_threshold=config_data.noise_reduction_threshold or "0.5",
        noise_reduction_prefix_padding_ms=config_data.noise_reduction_prefix_padding_ms or 300,
        noise_reduction_silence_duration_ms=config_data.noise_reduction_silence_duration_ms or 500,
        additional_settings=config_data.additional_settings or {}
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return config


@router.get("", response_model=List[AssistantConfigResponse])
async def list_assistants(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all assistant chatbots for current user"""
    configs = db.query(AssistantConfig).filter(
        AssistantConfig.user_id == current_user.id
    ).all()
    return configs


@router.get("/{assistant_id}", response_model=AssistantConfigResponse)
async def get_assistant(
    assistant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific assistant chatbot"""
    config = db.query(AssistantConfig).filter(
        AssistantConfig.id == assistant_id,
        AssistantConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found"
        )
    
    return config


@router.put("/{assistant_id}", response_model=AssistantConfigResponse)
async def update_assistant(
    assistant_id: int,
    config_data: AssistantConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update assistant configuration"""
    config = db.query(AssistantConfig).filter(
        AssistantConfig.id == assistant_id,
        AssistantConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found"
        )
    
    # Update fields
    update_data = config_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    
    return config


@router.delete("/{assistant_id}")
async def delete_assistant(
    assistant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an assistant chatbot"""
    config = db.query(AssistantConfig).filter(
        AssistantConfig.id == assistant_id,
        AssistantConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found"
        )
    
    db.delete(config)
    db.commit()
    return {"message": "Assistant deleted successfully"}


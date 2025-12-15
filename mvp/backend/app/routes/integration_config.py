"""
Third Party Service integration configuration routes (Chatbots)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.integration_config import IntegrationConfig
from app.schemas import (
    IntegrationConfigCreate, IntegrationConfigResponse, IntegrationConfigUpdate,IntegrationConfigMasked
)
from app.dependencies import get_current_user
from app.utils.encryption import encrypt_api_key, decrypt_api_key

router = APIRouter(prefix="/api/integration-config", tags=["integration_config"])


@router.post("")
async def create_integration_config(
    config_data: IntegrationConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new integration configuration"""
    encrypted_key = encrypt_api_key(config_data.encrypted_key)
    config = IntegrationConfig(
        provider=config_data.provider,
        instructions=config_data.instructions,
        encrypted_key=encrypted_key,
        is_active=True,
        user_id=current_user.id,
        agent_id = config_data.agent_id
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return config.id


@router.get("",response_model=List[IntegrationConfigResponse])
async def list_integration_config(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    """List all assistant chatbots for current user"""
    configs = db.query(IntegrationConfig).filter(
        IntegrationConfig.user_id == current_user.id,
        IntegrationConfig.agent_id == agent_id
    ).all()
    for config in configs:
        decrypted_key = decrypt_api_key(config.encrypted_key)
        config.masked_key = decrypted_key[:6]+ "x"* (len(decrypted_key)-9)+decrypted_key[-3:]

    return configs


@router.get("/{integration_config_id}",response_model =IntegrationConfigResponse)
async def get_integration_config(
    integration_config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific integration config """
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.id == integration_config_id,
        IntegrationConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration Config not found"
        )
    decrypted_key = decrypt_api_key(config.encrypted_key)
    config.masked_key = decrypted_key[:6]+ "x"* (len(decrypted_key)-9)+decrypted_key[-3:]

    return config


@router.put("/{integration_config_id}")
async def update_integration_config(
    integration_config_id: int,
    config_data: IntegrationConfigUpdate,
    db: Session = Depends(get_db)
):
    """Update assistant configuration"""
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.id == integration_config_id,
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration config not found"
        )
    
    # Update fields
    update_data = config_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    
    return config.id


@router.delete("/{integration_config_id}")
async def delete_integration_config(
    integration_config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete integration config"""
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.id == integration_config_id,
        IntegrationConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration config not found"
        )
    
    db.delete(config)
    db.commit()
    return {"message": "Integration config deleted successfully"}

@router.get("/{integration_config_id}/decrypted-key", response_model= IntegrationConfigMasked)
async def get_decrypted_integration_key(
    integration_config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get decrypted API key for a specific integration config """
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.id == integration_config_id,
        IntegrationConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration Config not found"
        )
    
    decrypted_key = decrypt_api_key(config.encrypted_key)
    return {"decrypted_key": decrypted_key}


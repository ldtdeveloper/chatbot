"""
OpenAI Key management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.openai_key import OpenAIKey
from app.schemas import OpenAIKeyCreate, OpenAIKeyResponse
from app.dependencies import get_current_user
from app.utils.encryption import encrypt_api_key, decrypt_api_key

router = APIRouter(prefix="/api/openai-keys", tags=["openai-keys"])


@router.post("", response_model=OpenAIKeyResponse)
async def create_openai_key(
    key_data: OpenAIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new OpenAI API key"""
    encrypted_key = encrypt_api_key(key_data.api_key)
    
    db_key = OpenAIKey(
        user_id=current_user.id,
        key_name=key_data.key_name,
        encrypted_key=encrypted_key
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    return db_key


@router.get("", response_model=List[OpenAIKeyResponse])
async def list_openai_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all OpenAI keys for current user"""
    keys = db.query(OpenAIKey).filter(OpenAIKey.user_id == current_user.id).all()
    return keys


@router.get("/{key_id}", response_model=OpenAIKeyResponse)
async def get_openai_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific OpenAI key"""
    key = db.query(OpenAIKey).filter(
        OpenAIKey.id == key_id,
        OpenAIKey.user_id == current_user.id
    ).first()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OpenAI key not found"
        )
    return key


@router.delete("/{key_id}")
async def delete_openai_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an OpenAI key"""
    key = db.query(OpenAIKey).filter(
        OpenAIKey.id == key_id,
        OpenAIKey.user_id == current_user.id
    ).first()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OpenAI key not found"
        )
    db.delete(key)
    db.commit()
    return {"message": "OpenAI key deleted successfully"}


@router.patch("/{key_id}/toggle")
async def toggle_openai_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle active status of an OpenAI key"""
    key = db.query(OpenAIKey).filter(
        OpenAIKey.id == key_id,
        OpenAIKey.user_id == current_user.id
    ).first()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OpenAI key not found"
        )
    key.is_active = not key.is_active
    db.commit()
    db.refresh(key)
    return key


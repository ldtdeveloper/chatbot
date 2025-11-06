"""
Prompt management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.prompt import Prompt, PromptVersion
from app.schemas import (
    PromptCreate, PromptResponse, PromptVersionCreate, PromptVersionResponse
)
from app.dependencies import get_current_user
import httpx
from app.config import settings

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.post("", response_model=PromptResponse)
async def create_prompt(
    prompt_data: PromptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new prompt"""
    db_prompt = Prompt(
        user_id=current_user.id,
        name=prompt_data.name,
        description=prompt_data.description
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    
    return db_prompt


@router.get("", response_model=List[PromptResponse])
async def list_prompts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all prompts for current user"""
    prompts = db.query(Prompt).filter(Prompt.user_id == current_user.id).all()
    return prompts


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific prompt with all versions"""
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.user_id == current_user.id
    ).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    return prompt


@router.post("/{prompt_id}/versions", response_model=PromptVersionResponse)
async def create_prompt_version(
    prompt_id: int,
    version_data: PromptVersionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new version of a prompt"""
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.user_id == current_user.id
    ).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    # Determine version number
    version_number = version_data.version_number
    if not version_number:
        existing_versions = db.query(PromptVersion).filter(
            PromptVersion.prompt_id == prompt_id
        ).order_by(PromptVersion.version_number.desc()).first()
        version_number = (existing_versions.version_number + 1) if existing_versions else 1
    
    db_version = PromptVersion(
        prompt_id=prompt_id,
        version_number=version_number,
        system_instructions=version_data.system_instructions
    )
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    
    # Update prompt's current version
    prompt.current_version = version_number
    db.commit()
    
    return db_version


@router.put("/{prompt_id}/versions/{version_id}", response_model=PromptVersionResponse)
async def update_prompt_version(
    prompt_id: int,
    version_id: int,
    version_data: PromptVersionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a prompt version"""
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.user_id == current_user.id
    ).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    version = db.query(PromptVersion).filter(
        PromptVersion.id == version_id,
        PromptVersion.prompt_id == prompt_id
    ).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt version not found"
        )
    
    version.system_instructions = version_data.system_instructions
    db.commit()
    db.refresh(version)
    
    return version


@router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a prompt and all its versions"""
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.user_id == current_user.id
    ).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    db.delete(prompt)
    db.commit()
    return {"message": "Prompt deleted successfully"}


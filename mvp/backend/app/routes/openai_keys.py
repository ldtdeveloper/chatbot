"""
OpenAI Key management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
# from app.models.openai_key import OpenAIKey
from app.models.agent import Agent
from app.models.interaction import Interaction
from app.models.user import User, UserRole  
# from app.schemas import OpenAIKeyCreate, OpenAIKeyResponse, OpenAIKeyMaskedResponse
from app.schemas import ServiceAccountKeyCreate,ServiceAccountKeyMaskedResponse,ServiceAccountKeyResponse
from app.models.service_account_key import ServiceAccountKey
from app.dependencies import get_current_user
from app.utils.encryption import encrypt_api_key, decrypt_api_key

router = APIRouter(prefix="/api/openai-keys", tags=["openai-keys"])


# @router.post("", response_model=OpenAIKeyResponse)
# async def create_openai_key(
#     key_data: OpenAIKeyCreate,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Create a new OpenAI API key"""
#     encrypted_key = encrypt_api_key(key_data.api_key)
    
#     db_key = OpenAIKey(
#         user_id=current_user.id,
#         key_name=key_data.key_name,
#         encrypted_key=encrypted_key
#     )
#     db.add(db_key)
#     db.commit()
#     db.refresh(db_key)
    
#     return db_key


# @router.get("", response_model=List[OpenAIKeyResponse])
# async def list_openai_keys(
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
    
#     """List all OpenAI keys for current user"""
#     if current_user.role=="superadmin":
#         keys = (
#             db.query(OpenAIKey)
            
#             .all()
#         )
#     else:
#         keys = db.query(OpenAIKey).filter(OpenAIKey.user_id == current_user.id).all()
#     return keys


# @router.get("/{key_id}", response_model=OpenAIKeyResponse)
# async def get_openai_key(
#     key_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Get a specific OpenAI key"""
#     key = db.query(OpenAIKey).filter(
#         OpenAIKey.id == key_id,
#         OpenAIKey.user_id == current_user.id
#     ).first()
#     if not key:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="OpenAI key not found"
#         )
#     return key


# @router.delete("/{key_id}")
# async def delete_openai_key(
#     key_id: int,
#     force: bool = Query(default=False, description="Force delete and cascade to agents/interactions"),
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Delete an OpenAI key
    
#     - If key is used by agents, returns error with list of agents
#     - Use force=true to cascade delete agents and interactions
#     """
#     key = db.query(OpenAIKey).filter(
#         OpenAIKey.id == key_id,
#         OpenAIKey.user_id == current_user.id
#     ).first()
#     if not key:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="OpenAI key not found"
#         )
    
#     # Check for dependent agents
#     agents = db.query(Agent).filter(Agent.openai_key_id == key_id).all()
    
#     # Check for dependent interactions
#     interactions = db.query(Interaction).filter(Interaction.openai_key_id == key_id).all()
    
#     if agents and not force:
#         agent_names = [a.name for a in agents]
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail={
#                 "message": f"Cannot delete key. It is used by {len(agents)} agent(s).",
#                 "agents": agent_names,
#                 "hint": "Delete the agents first, or use force=true to cascade delete"
#             }
#         )
    
#     # Force delete - cascade to agents and interactions
#     if force:
#         # Delete interactions first
#         for interaction in interactions:
#             db.delete(interaction)
        
#         # Delete agents
#         for agent in agents:
#             db.delete(agent)
    
#     # Delete the key
#     db.delete(key)
#     db.commit()
    
#     return {
#         "message": "OpenAI key deleted successfully",
#         "deleted_agents": len(agents) if force else 0,
#         "deleted_interactions": len(interactions) if force else 0
#     }


# @router.patch("/{key_id}/toggle")
# async def toggle_openai_key(
#     key_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Toggle active status of an OpenAI key"""
#     key = db.query(OpenAIKey).filter(
#         OpenAIKey.id == key_id,
#         OpenAIKey.user_id == current_user.id
#     ).first()
#     if not key:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="OpenAI key not found"
#         )
#     key.is_active = not key.is_active
#     db.commit()
#     db.refresh(key)
#     return key


# @router.get("/{key_id}/masked", response_model=OpenAIKeyMaskedResponse)
# async def get_masked_key(
#     key_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Get a masked version of the API key (first 8 and last 8 characters)"""
#     key = db.query(OpenAIKey).filter(
#         OpenAIKey.id == key_id,
#         OpenAIKey.user_id == current_user.id
#     ).first()
#     if not key:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="OpenAI key not found"
#         )
    
#     # Decrypt the key
#     decrypted_key = decrypt_api_key(key.encrypted_key)
    
#     # Mask the key: show first 8 and last 8 characters
#     if len(decrypted_key) <= 16:
#         # If key is too short, just show it partially
#         masked = decrypted_key[:4] + "..." + decrypted_key[-4:]
#     else:
#         masked = decrypted_key[:8] + "..." + decrypted_key[-8:]
    
#     return {"masked_key": masked}
"""
OpenAI Service Account Key management routes
"""
@router.post("", response_model=ServiceAccountKeyResponse)
async def create_service_account_key(
    key_data: ServiceAccountKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new service account key (admin or after payment)"""
    # Check if user already has one (unique per user)
    existing = db.query(ServiceAccountKey).filter(ServiceAccountKey.user_id == current_user.id).first()
    if existing:
        raise HTTPException(400, "User already has a service account key")

    # Generate key here (call your function)
    # For now, placeholder - replace with real generation
    db_key = ServiceAccountKey(
        user_id=current_user.id,
        email=current_user.email,
        key_name=key_data.key_name,
        service_account_key="sk-...",  
        openai_service_account_id="sa-...", 
        is_active=True
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    return db_key


@router.get("", response_model=List[ServiceAccountKeyResponse])
async def list_service_account_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all service account keys for current user"""
    if current_user.role == "superadmin":
        keys = db.query(ServiceAccountKey).all()
    else:
        keys = db.query(ServiceAccountKey).filter(ServiceAccountKey.user_id == current_user.id).all()
    return keys


@router.get("/{key_id}", response_model=ServiceAccountKeyResponse)
async def get_service_account_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific service account key"""
    key = db.query(ServiceAccountKey).filter(
        ServiceAccountKey.id == key_id,
        ServiceAccountKey.user_id == current_user.id
    ).first()
    if not key:
        raise HTTPException(status_code=404, detail="Service account key not found")
    return key


@router.delete("/{key_id}")
async def delete_service_account_key(
    key_id: int,
    force: bool = Query(default=False, description="Force delete and cascade to agents/interactions"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a service account key"""
    key = db.query(ServiceAccountKey).filter(
        ServiceAccountKey.id == key_id,
        ServiceAccountKey.user_id == current_user.id  # ← Fixed!
    ).first()
    if not key:
        raise HTTPException(status_code=404, detail="Service account key not found")
    
    # Check dependent agents
    agents = db.query(Agent).filter(Agent.service_account_id == key_id).all()
    
    # Check dependent interactions
    interactions = db.query(Interaction).filter(Interaction.service_account_id == key_id).all()
    
    if agents and not force:
        agent_names = [a.name for a in agents]
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Cannot delete key. Used by {len(agents)} agent(s).",
                "agents": agent_names,
                "hint": "Delete agents first or use force=true"
            }
        )
    
    if force:
        for interaction in interactions:
            db.delete(interaction)
        for agent in agents:
            db.delete(agent)
    
    db.delete(key)
    db.commit()
    
    return {
        "message": "Service account key deleted",
        "deleted_agents": len(agents) if force else 0,
        "deleted_interactions": len(interactions) if force else 0
    }
@router.patch("/{key_id}/toggle")
async def toggle_service_account_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"Toggle called for key_id: {key_id}, current user: {current_user.id} ({current_user.email})")
    
    query = db.query(ServiceAccountKey).filter(ServiceAccountKey.id == key_id)
    
    # Superadmin can toggle any key
    if current_user.role == UserRole.SUPERADMIN.value:
        print("Superadmin access - ignoring user_id filter")
    else:
        query = query.filter(ServiceAccountKey.user_id == current_user.id)
    
    key = query.first()
    
    print(f"Found key: {key}")
    if not key:
        print(f"No key found for id {key_id} and user {current_user.id}")
        raise HTTPException(404, "Service account key not found or you don't have access")
    
    key.is_active = not key.is_active
    print(f"New active status: {key.is_active}")
    
    db.commit()
    db.refresh(key)
    
    return key
@router.get("/{key_id}/masked", response_model=ServiceAccountKeyMaskedResponse)
async def get_masked_service_account_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get masked version of the service account key"""
    key = db.query(ServiceAccountKey).filter(
        ServiceAccountKey.id == key_id,
        ServiceAccountKey.user_id == current_user.id
    ).first()
    if not key:
        raise HTTPException(status_code=404, detail="Service account key not found")
    
    plain_key = key.service_account_key  # Plain field
    
    if len(plain_key) <= 16:
        masked = plain_key[:4] + "..." + plain_key[-4:]
    else:
        masked = plain_key[:8] + "..." + plain_key[-8:]
    
    return {
        "id": key.id,
        "key_name": key.key_name,
        "masked_key": masked,
        "openai_service_account_id": key.openai_service_account_id,
        "is_active": key.is_active,
        "created_at": key.created_at
    }
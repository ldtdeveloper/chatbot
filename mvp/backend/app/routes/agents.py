"""
Agent management routes - for managing Realtime Agent configurations
Based on OpenAI RealtimeAgent: https://openai.github.io/openai-agents-js/openai/agents-realtime/classes/realtimeagent/
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.agent import Agent, NoiseReductionMode, AgentType
from app.schemas.agents import (
    AgentCreate, AgentResponse, AgentUpdate
)

from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new agent configuration (stored locally)"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Creating agent for user {current_user.id} with data: {agent_data}")
    
    # Validate API key - System uses ServiceAccountKey (not OpenAIKey)
    # Note: Agent model has FK to openai_keys, but we're using ServiceAccountKey IDs
    from app.models.service_account_key import ServiceAccountKey
    api_key = db.query(ServiceAccountKey).filter(
        ServiceAccountKey.id == agent_data.openai_key_id,
        ServiceAccountKey.user_id == current_user.id,
        ServiceAccountKey.is_active
    ).first()
    
    logger.info(f"API key lookup: openai_key_id={agent_data.openai_key_id}, user_id={current_user.id}, found={api_key is not None}")
    
    if not api_key:
        # Check if key exists but belongs to different user or is inactive
        key_exists = db.query(ServiceAccountKey).filter(ServiceAccountKey.id == agent_data.openai_key_id).first()
        if key_exists:
            if key_exists.user_id != current_user.id:
                error_msg = f"API key {agent_data.openai_key_id} belongs to a different user"
            elif not key_exists.is_active:
                error_msg = f"API key {agent_data.openai_key_id} is inactive"
            else:
                error_msg = f"API key {agent_data.openai_key_id} is not accessible"
        else:
            error_msg = f"API key {agent_data.openai_key_id} does not exist"
        
        # Get available keys for better error message
        available_keys = db.query(ServiceAccountKey).filter(
            ServiceAccountKey.user_id == current_user.id,
            ServiceAccountKey.is_active
        ).all()
        
        available_key_ids = [str(k.id) for k in available_keys]
        if available_key_ids:
            error_msg += f". Available API keys for this user: {', '.join(available_key_ids)}"
        else:
            error_msg += ". Please create an OpenAI API key first."
        
        logger.warning(f"Invalid API key: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Check wallet balance for non-superadmin users - cannot create agent if balance is zero
    from app.models.user import UserRole
    agent_is_active = True
    if current_user.role != UserRole.SUPERADMIN:
        from app.utils.wallet import get_wallet_balance
        wallet_balance = get_wallet_balance(current_user.id, db)
        
        if wallet_balance <= 0:
            logger.warning(f"User {current_user.id} attempted to create agent with zero wallet balance (balance: ${wallet_balance:.2f})")
            raise HTTPException(
                status_code=402,  # Payment Required
                detail="Insufficient wallet balance. Please recharge your wallet to create new agents."
            )
        
        # Set agent active status based on wallet balance
        agent_is_active = wallet_balance > 0
    
    # Validate noise reduction mode
    noise_reduction = NoiseReductionMode.NEAR_FIELD
    if agent_data.noise_reduction_mode:
        try:
            # Convert string to enum, ensuring we use the value
            noise_reduction = NoiseReductionMode(agent_data.noise_reduction_mode)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid noise reduction mode. Must be one of: {[m.value for m in NoiseReductionMode]} or {[m.name for m in NoiseReductionMode]}"
            )
    
    # Create agent configuration (stored locally only)
    db_agent = Agent(
        user_id=current_user.id,
        openai_key_id=agent_data.openai_key_id,
        agent_type=AgentType.WEB,  # Default to WEB for website-based agents
        name=agent_data.name,
        domain=agent_data.domain,
        instructions=agent_data.instructions,
        voice=agent_data.voice or "alloy",
        noise_reduction_mode=noise_reduction.value,  # Use enum value explicitly
        noise_reduction_threshold=agent_data.noise_reduction_threshold or "0.5",
        noise_reduction_prefix_padding_ms=agent_data.noise_reduction_prefix_padding_ms or 300,
        noise_reduction_silence_duration_ms=agent_data.noise_reduction_silence_duration_ms or 500,
        agent_config=agent_data.agent_config or {},
        enable_mcp_server=agent_data.enable_mcp_server or False,
        is_active=agent_is_active
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    return db_agent


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    openai_key_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all agent configurations for current user"""
    query = db.query(Agent).filter(Agent.user_id == current_user.id)
    
    # Filter by API key if provided
    if openai_key_id:
        query = query.filter(Agent.openai_key_id == openai_key_id)
    
    agents = query.all()
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific agent configuration"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an agent configuration"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    update_dict = agent_data.dict(exclude_unset=True)  # Only include fields provided
     # Handle noise_reduction_mode separately for enum validation
    noise_mode_value = update_dict.get("noise_reduction_mode", None)
    if noise_mode_value is not None:
        try:
            noise_mode_enum = NoiseReductionMode(noise_mode_value)
            update_dict["noise_reduction_mode"] = noise_mode_enum.value
        except ValueError:
            allowed_values = [m.value for m in NoiseReductionMode]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid noise reduction mode. Must be one of: {allowed_values}"
            )

    # Apply updates dynamically
    for field, value in update_dict.items():
        setattr(agent, field, value)

    db.commit()
    db.refresh(agent)
    return agent


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an agent configuration"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    db.delete(agent)
    db.commit()
    return {"message": "Agent deleted successfully"}


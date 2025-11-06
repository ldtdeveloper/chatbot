"""
Agent management routes - for managing Realtime Agent configurations
Based on OpenAI RealtimeAgent: https://openai.github.io/openai-agents-js/openai/agents-realtime/classes/realtimeagent/
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.agent import Agent, NoiseReductionMode
from app.schemas import (
    AgentCreate, AgentResponse, AgentUpdate
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new agent configuration (stored locally)"""
    # Validate API key
    from app.models.openai_key import OpenAIKey
    api_key = db.query(OpenAIKey).filter(
        OpenAIKey.id == agent_data.openai_key_id,
        OpenAIKey.user_id == current_user.id,
        OpenAIKey.is_active == True
    ).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or inactive API key"
        )
    
    # Validate noise reduction mode
    noise_reduction = NoiseReductionMode.NEAR_FIELD
    if agent_data.noise_reduction_mode:
        try:
            noise_reduction = NoiseReductionMode(agent_data.noise_reduction_mode)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid noise reduction mode. Must be one of: {[m.value for m in NoiseReductionMode]}"
            )
    
    # Create agent configuration (stored locally only)
    db_agent = Agent(
        user_id=current_user.id,
        openai_key_id=agent_data.openai_key_id,
        name=agent_data.name,
        domain=agent_data.domain,
        instructions=agent_data.instructions,
        voice=agent_data.voice or "alloy",
        noise_reduction_mode=noise_reduction,
        noise_reduction_threshold=agent_data.noise_reduction_threshold or "0.5",
        noise_reduction_prefix_padding_ms=agent_data.noise_reduction_prefix_padding_ms or 300,
        noise_reduction_silence_duration_ms=agent_data.noise_reduction_silence_duration_ms or 500,
        agent_config=agent_data.agent_config or {}
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
    
    # Update fields if provided
    if agent_data.name is not None:
        agent.name = agent_data.name
    if agent_data.domain is not None:
        agent.domain = agent_data.domain
    if agent_data.instructions is not None:
        agent.instructions = agent_data.instructions
    if agent_data.voice is not None:
        agent.voice = agent_data.voice
    if agent_data.noise_reduction_mode is not None:
        try:
            agent.noise_reduction_mode = NoiseReductionMode(agent_data.noise_reduction_mode)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid noise reduction mode. Must be one of: {[m.value for m in NoiseReductionMode]}"
            )
    if agent_data.noise_reduction_threshold is not None:
        agent.noise_reduction_threshold = agent_data.noise_reduction_threshold
    if agent_data.noise_reduction_prefix_padding_ms is not None:
        agent.noise_reduction_prefix_padding_ms = agent_data.noise_reduction_prefix_padding_ms
    if agent_data.noise_reduction_silence_duration_ms is not None:
        agent.noise_reduction_silence_duration_ms = agent_data.noise_reduction_silence_duration_ms
    if agent_data.agent_config is not None:
        agent.agent_config = agent_data.agent_config
    
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


from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from openai import OpenAI
import logging
from sqlalchemy.orm import Session, joinedload
from app.utils.encryption import decrypt_api_key
from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.core.config import settings
from app.models.service_account_key import ServiceAccountKey
from app.models.text_agents import TextAgent
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai-chat"])


class AIChatRequest(BaseModel):
    text_agent_id: int = Field(..., description="ID from text_agents table")
    message: str = Field(..., min_length=1, description="User message to AI")
    model: str = Field("gpt-3.5-turbo", description="AI model to use (fixed default)")


class AIChatResponse(BaseModel):
    reply: str
    model_used: str
    success: bool = True
    error_message: Optional[str] = None


@router.post("/chat", response_model=AIChatResponse)
async def generate_ai_chat(
    req: AIChatRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    try:
        # ─────────────────────────────────────────────
        # 1. Fetch Text Agent + Owner (with eager loading)
        # ─────────────────────────────────────────────
        text_agent = (
            db.query(TextAgent)
            .options(joinedload(TextAgent.user))  # Load user relationship
            .filter(TextAgent.id == req.text_agent_id)
            .first()
        )

        if not text_agent:
            raise HTTPException(status_code=404, detail="Text agent not found")

        # Debug print (remove in production)
        print("TextAgent:", vars(text_agent))
        if text_agent.user:
            print("Owner:", vars(text_agent.user))

        # ─────────────────────────────────────────────
        # 2. Select API Key (Priority Order)
        # ─────────────────────────────────────────────
        api_key = None

        # Priority 1: Currently logged-in user (dashboard use)
        if current_user and current_user.service_account and current_user.service_account.service_account_key:
            api_key = decrypt_api_key(current_user.service_account.service_account_key)
            logger.debug(f"Using logged-in user key (user {current_user.id})")

        # Priority 2: Agent's specific service account key (assigned during creation)

        if not api_key and text_agent.openai_key_id:
            sa_key = db.query(ServiceAccountKey).filter(ServiceAccountKey.id == text_agent.openai_key_id).first()
            if sa_key and sa_key.service_account_key:
                api_key = decrypt_api_key(sa_key.service_account_key)
                logger.debug(f"Using agent-specific key (key_id {text_agent.openai_key_id})")

        # Priority 3: Owner of the text agent (fallback if no specific key)
        if not api_key and text_agent.user and text_agent.user.service_account and text_agent.user.service_account.service_account_key:
            api_key = decrypt_api_key(text_agent.user.service_account.service_account_key)
            logger.debug(f"Using agent owner key (user {text_agent.user.id})")

        if not api_key:
            logger.error("No OpenAI API key available at all")
            raise HTTPException(status_code=500, detail="No OpenAI API key configured")

        # ─────────────────────────────────────────────
        # 3. Build System Prompt
        # ─────────────────────────────────────────────
        system_prompt_parts = []

        # Agent-level instructions (main)
        if text_agent.instructions:
            system_prompt_parts.append(text_agent.instructions)

        # Default fallback

        # Default fallback
        if not system_prompt_parts:
            system_prompt_parts.append("You are a helpful assistant.")

        final_system_prompt = "\n\n".join(system_prompt_parts)

        # ─────────────────────────────────────────────
        # 4. Generate reply
        # ─────────────────────────────────────────────
        client = OpenAI(api_key=api_key)
        

        completion = client.chat.completions.create(
            model=req.model,
            messages=[
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": req.message}
            ],
            temperature=0.7,
            max_tokens=500
        )

        reply = completion.choices[0].message.content.strip()

        return AIChatResponse(
            reply=reply,
            model_used=req.model,
            success=True
        )

    except Exception as e:
        logger.exception("AI generation error")
        return AIChatResponse(
            reply="Sorry, something went wrong while generating reply.",
            model_used=req.model,
            success=False,
            error_message=str(e)
        )
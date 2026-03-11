from sqlalchemy.orm import Session
from openai import OpenAI
from app.models.text_agents import TextAgent
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


async def generate_ai_chat_logic(
    req: AIChatRequest,
    db: Session,
    api_key: str | None = None
) -> AIChatResponse:

    text_agent = db.query(TextAgent).filter(
        TextAgent.id == req.text_agent_id
    ).first()

    if not text_agent:
        return AIChatResponse(
            reply="Text agent not found",
            model_used=req.model,
            success=False
        )

    if not api_key:
        api_key = settings.MASTER_OPENAI_KEY

    client = OpenAI(api_key=api_key)

    try:
        completion = client.chat.completions.create(
            model=req.model,
            messages=[
                {"role": "system", "content": text_agent.instructions or "You are a helpful assistant."},
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
        logger.exception("OpenAI error")
        return AIChatResponse(
            reply="AI failed",
            model_used=req.model,
            success=False,
            error_message=str(e)
        )
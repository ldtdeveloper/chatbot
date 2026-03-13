from app.core.database import SessionLocal
from app.models.conversation import Conversation
from app.models.text_agents import TextAgent
from app.models.contact import Contact
from app.models.human_agent import HumanAgent
from sqlalchemy import or_

db = SessionLocal()
try:
    owner_id = 111
    # Mock current_agent["agent_id"] = 8 (from what we saw)
    agent_id = 8
    
    print(f"Testing query for owner_id={owner_id}, agent_id={agent_id}")
    
    active_conversations = (
        db.query(Conversation)
        .join(TextAgent, Conversation.text_agent_id == TextAgent.id)
        .filter(
            Conversation.is_human_active == True,
            TextAgent.user_id == owner_id,
            or_(
                Conversation.human_agent_id == None,
                Conversation.human_agent_id == agent_id
            )
        )
        .all()
    )
    
    print(f"Found {len(active_conversations)} conversations")
    for c in active_conversations:
        print(f"Convo ID: {c.id}, Human Active: {c.is_human_active}, Human Agent ID: {c.human_agent_id}")

finally:
    db.close()

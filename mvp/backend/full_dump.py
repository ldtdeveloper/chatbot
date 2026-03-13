from app.core.database import SessionLocal
from app.models.text_agents import TextAgent
from app.models.conversation import Conversation
import json

db = SessionLocal()
try:
    print("--- text_agents ---")
    agents = db.query(TextAgent).all()
    for a in agents:
        print(f"ID: {a.id}, UserID: {a.user_id}, Name: {a.name}, Active: {a.is_active}")

    print("\n--- conversations ---")
    convos = db.query(Conversation).all()
    for c in convos:
        print(f"ID: {c.id}, AgentID: {c.text_agent_id}, HumanActive: {c.is_human_active}, HumanAgentID: {c.human_agent_id}")

finally:
    db.close()

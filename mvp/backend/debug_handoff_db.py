from app.core.database import SessionLocal
from app.models.text_agents import TextAgent
from app.models.conversation import Conversation
from app.models.contact import Contact
from app.models.human_agent import HumanAgent

db = SessionLocal()
try:
    print("--- Agents ---")
    agents = db.query(TextAgent).filter(TextAgent.id == 8).all()
    for a in agents:
        print(f"Agent ID: {a.id}, User ID: {a.user_id}, Name: {a.name}")
    
    print("\n--- Human Agents (Employees) ---")
    human_agents = db.query(HumanAgent).filter(HumanAgent.user_id == 112).all()
    for ha in human_agents:
        print(f"Human Agent ID: {ha.id}, Name: {ha.name}, Owner ID: {ha.user_id}")

    print("\n--- Active Conversations for Owner 112 ---")
    convos = db.query(Conversation).join(TextAgent).filter(
        TextAgent.user_id == 112,
        Conversation.is_human_active == True
    ).all()
    
    if not convos:
        print("No active handover conversations found for user 112.")
    else:
        for c in convos:
            contact = db.query(Contact).filter(Contact.id == c.contact_id).first()
            print(f"Convo ID: {c.id}, Agent ID: {c.text_agent_id}, Contact: {contact.identifier if contact else 'None'}, Human Active: {c.is_human_active}, Assigned Agent: {c.human_agent_id}")

    print("\n--- All Conversations for Agent 8 ---")
    all_convos = db.query(Conversation).filter(Conversation.text_agent_id == 8).all()
    for c in all_convos:
        print(f"Convo ID: {c.id}, Human Active: {c.is_human_active}")

finally:
    db.close()

from app.core.database import SessionLocal
from app.models.text_agents import TextAgent
from app.models.conversation import Conversation
from app.models.contact import Contact
from app.models.human_agent import HumanAgent
from app.models.message import Message

db = SessionLocal()
try:
    print("--- Checking Agent 8 ---")
    agent = db.query(TextAgent).filter(TextAgent.id == 8).first()
    if agent:
        print(f"Agent ID: {agent.id}, User ID (Owner): {agent.user_id}, Name: {agent.name}")
    else:
        print("Agent 8 not found!")

    print("\n--- Checking Human Agent session context ---")
    # The user is connected as /dashboard/112
    owner_id = 112
    human_agents = db.query(HumanAgent).filter(HumanAgent.user_id == owner_id).all()
    print(f"Human agents for owner {owner_id}: {[ha.name for ha in human_agents]}")

    print(f"\n--- Checking Conversations for Agent 8 ---")
    convos = db.query(Conversation).filter(Conversation.text_agent_id == 8).all()
    print(f"Total conversations for Agent 8: {len(convos)}")
    for c in convos:
        contact = db.query(Contact).filter(Contact.id == c.contact_id).first()
        msg_count = db.query(Message).filter(Message.conversation_id == c.id).count()
        print(f"Convo ID: {c.id}, Contact: {contact.identifier if contact else 'Unknown'}, Human Active: {c.is_human_active}, Msg Count: {msg_count}, Assigned HaID: {c.human_agent_id}")

finally:
    db.close()

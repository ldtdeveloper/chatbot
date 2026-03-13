from app.core.database import SessionLocal
from app.models.text_agents import TextAgent
from app.models.conversation import Conversation
from app.models.contact import Contact
from app.models.message import Message
from datetime import datetime

db = SessionLocal()
try:
    # Use Agent 8 which we know belongs to 111
    agent_id = 8
    
    # 1. Create a dummy contact
    contact_id_str = "TestUser-" + datetime.utcnow().strftime("%H%M%S")
    contact = Contact(identifier=contact_id_str)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    print(f"Created contact: {contact.id} ({contact.identifier})")

    # 2. Create conversation
    convo = Conversation(
        contact_id=contact.id,
        text_agent_id=agent_id,
        is_human_active=True
    )
    db.add(convo)
    db.commit()
    db.refresh(convo)
    print(f"Created conversation: {convo.id}")

    # 3. Add a message
    msg = Message(
        conversation_id=convo.id,
        content="Testing handoff visibility manual",
        is_from_contact=True
    )
    db.add(msg)
    db.commit()
    print("Added message. Dashboard 111 should now see this chat on refresh.")

finally:
    db.close()

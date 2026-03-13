from app.core.database import SessionLocal
from app.models.text_agents import TextAgent
from app.models.whatsapp_configs import WhatsappConfig
from app.models.conversation import Conversation
from app.models.contact import Contact

db = SessionLocal()
try:
    print("--- All Text Agents ---")
    agents = db.query(TextAgent).all()
    for a in agents:
        config = db.query(WhatsappConfig).filter(WhatsappConfig.text_agent_id == a.id).first()
        print(f"Agent ID: {a.id}, Owner: {a.user_id}, Name: {a.name}, Phone Number ID: {config.phone_number_id if config else 'None'}")

    print("\n--- All Conversations ---")
    convos = db.query(Conversation).all()
    for c in convos:
        print(f"Convo ID: {c.id}, Agent ID: {c.text_agent_id}, Human Active: {c.is_human_active}")

    print("\n--- Recent Contacts ---")
    contacts = db.query(Contact).all()
    for con in contacts:
        print(f"Contact ID: {con.id}, Identifier: {con.identifier}")

finally:
    db.close()

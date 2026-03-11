from app.core.database import SessionLocal
from app.models.text_agents import TextAgent

db = SessionLocal()
try:
    a8 = db.query(TextAgent).filter(TextAgent.id == 8).first()
    if a8:
        print(f"AGENT_8_OWNER_ID: {a8.user_id}")
    else:
        print("AGENT_8_NOT_FOUND")
    
    agents = db.query(TextAgent).all()
    for a in agents:
        print(f"AGENT_ID: {a.id}, OWNER_ID: {a.user_id}, NAME: {a.name}")
finally:
    db.close()

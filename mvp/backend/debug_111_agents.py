from app.core.database import SessionLocal
from app.models.text_agents import TextAgent

db = SessionLocal()
try:
    print("--- Agents belonging to User 111 ---")
    agents111 = db.query(TextAgent).filter(TextAgent.user_id == 111).all()
    for a in agents111:
        print(f"ID: {a.id}, Name: {a.name}")
    
    print("\n--- Agents belonging to User 112 ---")
    agents112 = db.query(TextAgent).filter(TextAgent.user_id == 112).all()
    for a in agents112:
        print(f"ID: {a.id}, Name: {a.name}")
finally:
    db.close()

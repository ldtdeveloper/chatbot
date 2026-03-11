from app.core.database import SessionLocal
from app.models.text_agents import TextAgent
from app.models.user import User
from app.models.human_agent import HumanAgent

db = SessionLocal()
try:
    print("--- Users ---")
    u111 = db.query(User).filter(User.id == 111).first()
    u112 = db.query(User).filter(User.id == 112).first()
    if u111: print(f"User 111: {u111.email}, Role: {u111.role}")
    if u112: print(f"User 112: {u112.email}, Role: {u112.role}")

    print("\n--- Text Agent 8 ---")
    agent = db.query(TextAgent).filter(TextAgent.id == 8).first()
    if agent:
        print(f"Agent 8 ID: {agent.id}, Owner User ID: {agent.user_id}, Name: {agent.name}")

    print("\n--- All Text Agents ---")
    agents = db.query(TextAgent).all()
    for a in agents:
        print(f"Agent ID: {a.id}, Owner User ID: {a.user_id}, Name: {a.name}")

    print("\n--- Human Agents (Employees) ---")
    ha111 = db.query(HumanAgent).filter(HumanAgent.user_id == 111).all()
    ha112 = db.query(HumanAgent).filter(HumanAgent.user_id == 112).all()
    print(f"Employees for 111: {[ha.name for ha in ha111]}")
    print(f"Employees for 112: {[ha.name for ha in ha112]}")

finally:
    db.close()

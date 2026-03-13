from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ldtchat")

engine = create_engine(database_url)

agent_id = 7

with engine.connect() as conn:
    # Check TextAgent
    res = conn.execute(text("SELECT id, name, channel, user_id FROM text_agents WHERE id = :id"), {"id": agent_id}).fetchone()
    print(f"Agent ID: {agent_id}")
    if res:
        print(f"Agent Name: {res[1]}")
        print(f"Channel: {res[2]}")
        print(f"User ID: {res[3]}")
    else:
        print("Agent not found!")

    # Check WhatsappConfig
    res = conn.execute(text("SELECT id, phone_number_id, phone_number, access_token FROM whatsapp_configs WHERE text_agent_id = :id"), {"id": agent_id}).fetchone()
    if res:
        print(f"Config ID: {res[0]}")
        print(f"Phone Number ID: {res[1]}")
        print(f"Phone Number: {res[2]}")
        print(f"Access Token exists: {bool(res[3])}")
    else:
        print("WhatsappConfig NOT FOUND for this agent!")

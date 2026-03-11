from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("DATABASE_URL not found in .env")
    exit(1)

engine = create_engine(database_url)

with engine.connect() as conn:
    print("Listing all WhatsApp Configs:")
    query = text("SELECT id, text_agent_id, phone_number_id, phone_number, LEFT(access_token, 10) as token_start, LENGTH(access_token) as token_len FROM whatsapp_configs")
    res = conn.execute(query).fetchall()
    for row in res:
        print(f"ID: {row[0]} | AgentID: {row[1]} | PhoneID: {row[2]} | Phone: {row[3]} | TokenStart: {row[4]} | TokenLen: {row[5]}")

    print("\nChecking Agent 7 specifically:")
    res_agent = conn.execute(text("SELECT id, name FROM text_agents WHERE id = 7")).fetchone()
    if res_agent:
        print(f"Agent 7 Name: {res_agent[1]}")
    else:
        print("Agent 7 not found in text_agents")

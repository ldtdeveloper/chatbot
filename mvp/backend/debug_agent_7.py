import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend app to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

from core.config import settings
from models.text_agents import TextAgent
from models.whatsapp_configs import WhatsappConfig

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

agent_id = 7
agent = db.query(TextAgent).filter(TextAgent.id == agent_id).first()
config = db.query(WhatsappConfig).filter(WhatsappConfig.text_agent_id == agent_id).first()

print(f"Agent ID: {agent_id}")
if agent:
    print(f"Agent Name: {agent.name}")
    print(f"Channel: {agent.channel}")
    print(f"User ID: {agent.user_id}")
else:
    print("Agent not found!")

if config:
    print(f"Config ID: {config.id}")
    print(f"Phone Number ID: {config.phone_number_id}")
    print(f"Phone Number: {config.phone_number}")
    print(f"Access Token exists: {bool(config.access_token)}")
else:
    print("WhatsappConfig NOT FOUND for this agent!")

db.close()

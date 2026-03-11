import os
import sys
from sqlalchemy import create_engine, text

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app.core.config import settings

def migrate():
    # Use the database URL from settings
    db_url = settings.database_url
    if "+psycopg2" not in db_url and "postgresql" in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")
    
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("Checking for openai_key_id in text_agents table...")
        # Check if column exists
        # In Postgres, we can check information_schema
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='text_agents' AND column_name='openai_key_id'"))
        if not result.fetchone():
            print("Adding column openai_key_id to text_agents...")
            try:
                conn.execute(text("ALTER TABLE text_agents ADD COLUMN openai_key_id INTEGER REFERENCES service_account_key(id)"))
                conn.commit()
                print("Successfully added openai_key_id column.")
            except Exception as e:
                print(f"Error adding column: {e}")
                conn.rollback()
        else:
            print("Column openai_key_id already exists.")

if __name__ == "__main__":
    migrate()

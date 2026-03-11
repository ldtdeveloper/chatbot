from sqlalchemy import text
from app.core.database import engine

def fix_enum():
    with engine.connect() as conn:
        print("Checking agenttype enum...")
        try:
            # PostgreSQL command to add a value to an enum
            # Note: This cannot be run inside a transaction block in some PG versions, 
            # but SQLAlchemy connect() usually handles this or we can use execution_options
            conn.execute(text("ALTER TYPE agenttype ADD VALUE IF NOT EXISTS 'WHATSAPP'"))
            conn.commit()
            print("Successfully added 'WHATSAPP' to agenttype enum.")
        except Exception as e:
            print(f"Error or already exists: {e}")

if __name__ == "__main__":
    fix_enum()

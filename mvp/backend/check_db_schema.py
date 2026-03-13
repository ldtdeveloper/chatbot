from sqlalchemy import create_engine, inspect
import sys
import os

# Add the current directory to path so we can import app
sys.path.append(os.getcwd())

from app.core.config import settings

def check_columns():
    engine = create_engine(settings.database_url)
    inspector = inspect(engine)
    
    for table_name in ["users", "text_agents", "conversations"]:
        print(f"\nColumns in table '{table_name}':")
        columns = inspector.get_columns(table_name)
        for column in columns:
            print(f" - {column['name']} ({column['type']})")

if __name__ == "__main__":
    check_columns()

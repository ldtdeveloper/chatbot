"""
Migration script to create/recreate the interactions table
Run this once to set up the interactions table for dashboard analytics
"""
from app.database import engine, Base
from app.models.interaction import Interaction
from sqlalchemy import text, inspect

def migrate():
    """Create or recreate the interactions table"""
    inspector = inspect(engine)
    
    # Check if interactions table exists
    if 'interactions' in inspector.get_table_names():
        print("Dropping existing interactions table...")
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS interactions CASCADE"))
            conn.commit()
        print("Dropped interactions table")
    
    # Create the interactions table with the new schema
    print("Creating interactions table...")
    Interaction.__table__.create(engine)
    print("Created interactions table successfully!")
    
    # Verify the table was created
    inspector = inspect(engine)
    if 'interactions' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('interactions')]
        print(f"Interactions table columns: {columns}")
    else:
        print("ERROR: Table was not created!")

if __name__ == "__main__":
    migrate()


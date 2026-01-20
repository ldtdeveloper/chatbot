"""
Migration script to add startup_message column to agents table
"""
import sys
from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.core.config import settings

def migrate_add_startup_message():
    """Add startup_message column to agents table"""
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Migration: Adding startup_message column to agents table")
        print("=" * 60)
        
        if is_postgres:
            # PostgreSQL
            print("\n[1/2] Checking if startup_message column exists...")
            check_column = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='agents' AND column_name='startup_message'
            """)
            result = db.execute(check_column).fetchone()
            
            if result:
                print("⚠️  Column 'startup_message' already exists. Skipping column creation.")
            else:
                print("\n[2/2] Adding startup_message column...")
                add_column = text("""
                    ALTER TABLE agents 
                    ADD COLUMN startup_message TEXT
                """)
                db.execute(add_column)
                db.commit()
                print("✅ Column 'startup_message' added successfully")
        else:
            # SQLite
            print("\n[1/2] Checking if startup_message column exists...")
            check_column = text("""
                PRAGMA table_info(agents)
            """)
            result = db.execute(check_column).fetchall()
            columns = [row[1] for row in result]
            
            if 'startup_message' in columns:
                print("⚠️  Column 'startup_message' already exists. Skipping column creation.")
            else:
                print("\n[2/2] Adding startup_message column...")
                add_column = text("""
                    ALTER TABLE agents 
                    ADD COLUMN startup_message TEXT
                """)
                try:
                    db.execute(add_column)
                    db.commit()
                    print("✅ Column 'startup_message' added successfully")
                except Exception as e:
                    print(f"❌ Error adding column: {e}")
                    raise
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    migrate_add_startup_message()

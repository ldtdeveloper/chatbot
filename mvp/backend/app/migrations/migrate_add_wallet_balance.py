"""
Migration script to add wallet_balance column to users table
"""
import sys
from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.core.config import settings

def migrate_add_wallet_balance():
    """Add wallet_balance column to users table"""
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Migration: Adding wallet_balance column to users table")
        print("=" * 60)
        
        if is_postgres:
            # PostgreSQL
            print("\n[1/2] Checking if wallet_balance column exists...")
            check_column = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='wallet_balance'
            """)
            result = db.execute(check_column).fetchone()
            
            if result:
                print("⚠️  Column 'wallet_balance' already exists. Skipping column creation.")
            else:
                print("\n[2/2] Adding wallet_balance column...")
                add_column = text("""
                    ALTER TABLE users 
                    ADD COLUMN wallet_balance FLOAT DEFAULT 0.0
                """)
                db.execute(add_column)
                db.commit()
                print("✅ Column 'wallet_balance' added successfully")
        else:
            # SQLite
            print("\n[1/2] Checking if wallet_balance column exists...")
            check_column = text("""
                PRAGMA table_info(users)
            """)
            result = db.execute(check_column).fetchall()
            columns = [row[1] for row in result]
            
            if 'wallet_balance' in columns:
                print("⚠️  Column 'wallet_balance' already exists. Skipping column creation.")
            else:
                print("\n[2/2] Adding wallet_balance column...")
                add_column = text("""
                    ALTER TABLE users 
                    ADD COLUMN wallet_balance FLOAT DEFAULT 0.0
                """)
                try:
                    db.execute(add_column)
                    db.commit()
                    print("✅ Column 'wallet_balance' added successfully")
                except Exception as e:
                    print(f"❌ Error adding column: {e}")
                    raise
        
        # Verify the column
        verify_query = text("""
            SELECT COUNT(*) as total_users,
                   COUNT(CASE WHEN wallet_balance IS NOT NULL THEN 1 END) as with_wallet
            FROM users
        """)
        verify_result = db.execute(verify_query).fetchone()
        
        print("\n" + "=" * 60)
        print("Migration Summary:")
        print("=" * 60)
        print(f"Total users: {verify_result[0]}")
        print(f"Users with wallet_balance: {verify_result[1]}")
        print("=" * 60)
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    migrate_add_wallet_balance()

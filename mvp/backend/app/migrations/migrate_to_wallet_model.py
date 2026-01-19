"""
Migration script to create wallets table and migrate data from wallet_balance column
This will:
1. Create wallets table
2. Migrate existing wallet_balance data to wallets table (keeping old users at 0)
3. Optionally remove wallet_balance column from users table (commented out for safety)
"""
import sys
from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.core.config import settings

def migrate_to_wallet_model():
    """Create wallets table and migrate data"""
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Migration: Creating wallets table and migrating data")
        print("=" * 60)
        
        if is_postgres:
            # PostgreSQL
            print("\n[1/3] Checking if wallets table exists...")
            check_table = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'wallets'
                )
            """)
            result = db.execute(check_table).fetchone()
            
            if result and result[0]:
                print("⚠️  Table 'wallets' already exists. Skipping table creation.")
            else:
                print("\n[2/3] Creating wallets table...")
                create_table = text("""
                    CREATE TABLE wallets (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER UNIQUE NOT NULL,
                        balance FLOAT DEFAULT 0.0 NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE,
                        CONSTRAINT fk_wallet_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
                db.execute(create_table)
                db.commit()
                print("✅ Table 'wallets' created successfully")
            
            # Check if wallet_balance column exists in users table
            print("\n[3/3] Migrating data from wallet_balance column...")
            check_column = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='wallet_balance'
            """)
            column_result = db.execute(check_column).fetchone()
            
            if column_result:
                # Migrate data: For old users, set balance to 0.0 (as requested)
                # Only migrate if wallet doesn't exist for user
                migrate_data = text("""
                    INSERT INTO wallets (user_id, balance, created_at)
                    SELECT id, 0.0, created_at
                    FROM users
                    WHERE id NOT IN (SELECT user_id FROM wallets)
                """)
                db.execute(migrate_data)
                db.commit()
                print("✅ Migrated wallet data (old users set to 0.0 balance)")
            else:
                # No wallet_balance column, just create wallets for existing users
                create_wallets = text("""
                    INSERT INTO wallets (user_id, balance, created_at)
                    SELECT id, 0.0, created_at
                    FROM users
                    WHERE id NOT IN (SELECT user_id FROM wallets)
                """)
                db.execute(create_wallets)
                db.commit()
                print("✅ Created wallets for existing users (all set to 0.0 balance)")
        else:
            # SQLite
            print("\n[1/3] Checking if wallets table exists...")
            check_table = text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='wallets'
            """)
            result = db.execute(check_table).fetchone()
            
            if result:
                print("⚠️  Table 'wallets' already exists. Skipping table creation.")
            else:
                print("\n[2/3] Creating wallets table...")
                create_table = text("""
                    CREATE TABLE wallets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE NOT NULL,
                        balance REAL DEFAULT 0.0 NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
                db.execute(create_table)
                db.commit()
                print("✅ Table 'wallets' created successfully")
            
            # Migrate data
            print("\n[3/3] Migrating data...")
            create_wallets = text("""
                INSERT INTO wallets (user_id, balance, created_at)
                SELECT id, 0.0, created_at
                FROM users
                WHERE id NOT IN (SELECT user_id FROM wallets)
            """)
            db.execute(create_wallets)
            db.commit()
            print("✅ Created wallets for existing users (all set to 0.0 balance)")
        
        # Verify the migration
        verify_query = text("""
            SELECT COUNT(*) as total_users,
                   (SELECT COUNT(*) FROM wallets) as total_wallets
            FROM users
        """)
        verify_result = db.execute(verify_query).fetchone()
        
        print("\n" + "=" * 60)
        print("Migration Summary:")
        print("=" * 60)
        print(f"Total users: {verify_result[0]}")
        print(f"Total wallets: {verify_result[1]}")
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print("\nNote: wallet_balance column still exists in users table.")
        print("You can remove it manually after verifying the migration.")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    migrate_to_wallet_model()

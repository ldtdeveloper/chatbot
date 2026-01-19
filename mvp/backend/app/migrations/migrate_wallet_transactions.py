"""
Migration script to create wallet_transactions table
"""
import sys
from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.core.config import settings

def migrate_wallet_transactions():
    """Create wallet_transactions table"""
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Migration: Creating wallet_transactions table")
        print("=" * 60)
        
        if is_postgres:
            # PostgreSQL
            print("\n[1/2] Checking if wallet_transactions table exists...")
            check_table = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'wallet_transactions'
                )
            """)
            result = db.execute(check_table).fetchone()
            
            if result and result[0]:
                print("⚠️  Table 'wallet_transactions' already exists. Skipping table creation.")
            else:
                print("\n[2/2] Creating wallet_transactions table...")
                create_table = text("""
                    CREATE TABLE wallet_transactions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        amount FLOAT NOT NULL,
                        razorpay_order_id VARCHAR(255),
                        razorpay_payment_id VARCHAR(255),
                        razorpay_signature VARCHAR(255),
                        status VARCHAR(50) DEFAULT 'pending' NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE,
                        CONSTRAINT fk_wallet_transaction_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
                db.execute(create_table)
                
                # Create index on user_id
                create_index = text("""
                    CREATE INDEX IF NOT EXISTS idx_wallet_transactions_user_id ON wallet_transactions(user_id)
                """)
                db.execute(create_index)
                
                # Create index on razorpay_order_id
                create_index2 = text("""
                    CREATE INDEX IF NOT EXISTS idx_wallet_transactions_order_id ON wallet_transactions(razorpay_order_id)
                """)
                db.execute(create_index2)
                
                db.commit()
                print("✅ Table 'wallet_transactions' created successfully")
        else:
            # SQLite
            print("\n[1/2] Checking if wallet_transactions table exists...")
            check_table = text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='wallet_transactions'
            """)
            result = db.execute(check_table).fetchone()
            
            if result:
                print("⚠️  Table 'wallet_transactions' already exists. Skipping table creation.")
            else:
                print("\n[2/2] Creating wallet_transactions table...")
                create_table = text("""
                    CREATE TABLE wallet_transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        amount REAL NOT NULL,
                        razorpay_order_id TEXT,
                        razorpay_payment_id TEXT,
                        razorpay_signature TEXT,
                        status TEXT DEFAULT 'pending' NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
                db.execute(create_table)
                
                # Create indexes
                create_index = text("""
                    CREATE INDEX IF NOT EXISTS idx_wallet_transactions_user_id ON wallet_transactions(user_id)
                """)
                db.execute(create_index)
                
                create_index2 = text("""
                    CREATE INDEX IF NOT EXISTS idx_wallet_transactions_order_id ON wallet_transactions(razorpay_order_id)
                """)
                db.execute(create_index2)
                
                db.commit()
                print("✅ Table 'wallet_transactions' created successfully")
        
        # Verify the table
        verify_query = text("""
            SELECT COUNT(*) as total_transactions
            FROM wallet_transactions
        """)
        verify_result = db.execute(verify_query).fetchone()
        
        print("\n" + "=" * 60)
        print("Migration Summary:")
        print("=" * 60)
        print(f"Total wallet transactions: {verify_result[0]}")
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
    migrate_wallet_transactions()

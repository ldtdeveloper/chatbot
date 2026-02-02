"""
Migration script to update plans table schema:
- Remove 'code' column
- Rename 'credits' to 'wallet_credits'
- Add 'currency' column (default: USD)
- Add 'plan_type' column (default: monthly)
"""
import sys
from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.core.config import settings

def migrate_plans_schema():
    """Update plans table schema"""
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Migration: Updating plans table schema")
        print("=" * 60)
        
        if is_postgres:
            # PostgreSQL
            print("\n[1/5] Checking if plans table exists...")
            check_table = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'plans'
                )
            """)
            result = db.execute(check_table).fetchone()
            
            if not result or not result[0]:
                print("⚠️  Table 'plans' does not exist. Skipping migration.")
                return
            
            # Check and add currency column
            print("\n[2/5] Adding 'currency' column...")
            check_currency = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='plans' AND column_name='currency'
            """)
            result = db.execute(check_currency).fetchone()
            if not result:
                add_currency = text("""
                    ALTER TABLE plans 
                    ADD COLUMN currency VARCHAR(10)
                """)
                db.execute(add_currency)
                # Update existing rows to have USD as default
                update_currency = text("""
                    UPDATE plans 
                    SET currency = 'USD' 
                    WHERE currency IS NULL
                """)
                db.execute(update_currency)
                # Now make it NOT NULL
                alter_currency_not_null = text("""
                    ALTER TABLE plans 
                    ALTER COLUMN currency SET NOT NULL,
                    ALTER COLUMN currency SET DEFAULT 'USD'
                """)
                db.execute(alter_currency_not_null)
                db.commit()
                print("✅ Added 'currency' column")
            else:
                print("⚠️  'currency' column already exists")
            
            # Check and add plan_type column
            print("\n[3/5] Adding 'plan_type' column...")
            check_plan_type = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='plans' AND column_name='plan_type'
            """)
            result = db.execute(check_plan_type).fetchone()
            if not result:
                add_plan_type = text("""
                    ALTER TABLE plans 
                    ADD COLUMN plan_type VARCHAR(20)
                """)
                db.execute(add_plan_type)
                # Update existing rows to have monthly as default
                update_plan_type = text("""
                    UPDATE plans 
                    SET plan_type = 'monthly' 
                    WHERE plan_type IS NULL
                """)
                db.execute(update_plan_type)
                # Now make it NOT NULL
                alter_plan_type_not_null = text("""
                    ALTER TABLE plans 
                    ALTER COLUMN plan_type SET NOT NULL,
                    ALTER COLUMN plan_type SET DEFAULT 'monthly'
                """)
                db.execute(alter_plan_type_not_null)
                db.commit()
                print("✅ Added 'plan_type' column")
            else:
                print("⚠️  'plan_type' column already exists")
            
            # Rename credits to wallet_credits
            print("\n[4/5] Renaming 'credits' to 'wallet_credits'...")
            check_credits = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='plans' AND column_name='credits'
            """)
            result = db.execute(check_credits).fetchone()
            if result:
                check_wallet_credits = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='plans' AND column_name='wallet_credits'
                """)
                result2 = db.execute(check_wallet_credits).fetchone()
                if not result2:
                    rename_credits = text("""
                        ALTER TABLE plans 
                        RENAME COLUMN credits TO wallet_credits
                    """)
                    db.execute(rename_credits)
                    db.commit()
                    print("✅ Renamed 'credits' to 'wallet_credits'")
                else:
                    print("⚠️  'wallet_credits' already exists, keeping both columns")
            else:
                print("⚠️  'credits' column does not exist")
            
            # Remove code column if it exists
            print("\n[5/5] Removing 'code' column...")
            check_code = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='plans' AND column_name='code'
            """)
            result = db.execute(check_code).fetchone()
            if result:
                drop_code = text("""
                    ALTER TABLE plans 
                    DROP COLUMN IF EXISTS code
                """)
                db.execute(drop_code)
                db.commit()
                print("✅ Removed 'code' column")
            else:
                print("⚠️  'code' column does not exist")
        
        else:
            # SQLite
            print("\n[1/5] Checking if plans table exists...")
            check_table = text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='plans'
            """)
            result = db.execute(check_table).fetchone()
            
            if not result:
                print("⚠️  Table 'plans' does not exist. Skipping migration.")
                return
            
            # SQLite doesn't support ALTER TABLE ADD COLUMN with DEFAULT easily
            # We'll need to recreate the table or use a workaround
            print("\n⚠️  SQLite detected. Manual migration may be required.")
            print("   Please ensure the following columns exist:")
            print("   - currency (VARCHAR, default 'USD')")
            print("   - plan_type (VARCHAR, default 'monthly')")
            print("   - wallet_credits (INTEGER, renamed from credits)")
            print("   - Remove 'code' column if it exists")
        
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
    migrate_plans_schema()

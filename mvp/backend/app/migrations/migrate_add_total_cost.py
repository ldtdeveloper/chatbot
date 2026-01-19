"""
Migration script to add total_cost column to interactions table
and update existing records with calculated values (estimated_cost * 1.1)
"""
import sys
from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.core.config import settings

def migrate_add_total_cost():
    """Add total_cost column and update existing records"""
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Migration: Adding total_cost column to interactions table")
        print("=" * 60)
        
        if is_postgres:
            # PostgreSQL
            print("\n[1/3] Checking if total_cost column exists...")
            check_column = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='interactions' AND column_name='total_cost'
            """)
            result = db.execute(check_column).fetchone()
            
            if result:
                print("⚠️  Column 'total_cost' already exists. Skipping column creation.")
            else:
                print("\n[2/3] Adding total_cost column...")
                add_column = text("""
                    ALTER TABLE interactions 
                    ADD COLUMN total_cost FLOAT DEFAULT 0.0
                """)
                db.execute(add_column)
                db.commit()
                print("✅ Column 'total_cost' added successfully")
        else:
            # SQLite
            print("\n[1/3] Checking if total_cost column exists...")
            check_column = text("""
                PRAGMA table_info(interactions)
            """)
            result = db.execute(check_column).fetchall()
            columns = [row[1] for row in result]
            
            if 'total_cost' in columns:
                print("⚠️  Column 'total_cost' already exists. Skipping column creation.")
            else:
                print("\n[2/3] Adding total_cost column...")
                # SQLite doesn't support ALTER TABLE ADD COLUMN with DEFAULT easily
                # We'll need to recreate the table or use a workaround
                print("⚠️  SQLite detected. Adding column...")
                add_column = text("""
                    ALTER TABLE interactions 
                    ADD COLUMN total_cost FLOAT DEFAULT 0.0
                """)
                try:
                    db.execute(add_column)
                    db.commit()
                    print("✅ Column 'total_cost' added successfully")
                except Exception as e:
                    print(f"❌ Error adding column: {e}")
                    print("Note: SQLite may require table recreation for some operations")
                    raise
        
        print("\n[3/3] Updating existing records with total_cost = estimated_cost * 1.1...")
        if is_postgres:
            # PostgreSQL requires casting to numeric for ROUND
            update_query = text("""
                UPDATE interactions 
                SET total_cost = ROUND((estimated_cost * 1.1)::numeric, 6)::float
                WHERE estimated_cost IS NOT NULL AND estimated_cost > 0
            """)
        else:
            # SQLite
            update_query = text("""
                UPDATE interactions 
                SET total_cost = ROUND(estimated_cost * 1.1, 6)
                WHERE estimated_cost IS NOT NULL AND estimated_cost > 0
            """)
        result = db.execute(update_query)
        db.commit()
        updated_count = result.rowcount
        print(f"✅ Updated {updated_count} existing records")
        
        # Verify the update
        verify_query = text("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN total_cost > 0 THEN 1 END) as with_total_cost,
                   SUM(estimated_cost) as total_estimated,
                   SUM(total_cost) as total_cost_sum
            FROM interactions
        """)
        verify_result = db.execute(verify_query).fetchone()
        
        print("\n" + "=" * 60)
        print("Migration Summary:")
        print("=" * 60)
        print(f"Total interactions: {verify_result[0]}")
        print(f"Records with total_cost: {verify_result[1]}")
        print(f"Total estimated_cost: ${verify_result[2] or 0:.6f}")
        print(f"Total total_cost: ${verify_result[3] or 0:.6f}")
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
    migrate_add_total_cost()

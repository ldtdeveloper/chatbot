"""
Migration script to update agents table foreign key from openai_keys.id to service_account_key.id
"""
import sys
from sqlalchemy import text
from app.database import engine
from app.config import settings

def migrate_agent_foreign_key():
    """Update agents table foreign key constraint"""
    
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    if not is_postgres:
        print("   ⏭️  Skipping foreign key migration (non-PostgreSQL database)")
        return
    
    print("   🔄 Migrating agents table foreign key constraint...")
    print("      From: openai_keys.id")
    print("      To: service_account_key.id")
    
    with engine.begin() as conn:  # Use begin() for automatic transaction management
        try:
            # Check if agents table exists
            check_table = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'agents'
                )
            """)
            result = conn.execute(check_table)
            table_exists = result.scalar()
            
            if not table_exists:
                print("      ⏭️  Agents table doesn't exist yet (will be created with correct constraint)")
                return
            
            # Check if old constraint exists
            check_constraint = text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'agents' 
                AND constraint_type = 'FOREIGN KEY'
                AND constraint_name = 'agents_openai_key_id_fkey'
            """)
            result = conn.execute(check_constraint)
            old_constraint = result.fetchone()
            
            # Check what table the constraint currently references
            if old_constraint:
                check_referenced_table = text("""
                    SELECT 
                        tc.table_name, 
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_name = 'agents_openai_key_id_fkey'
                """)
                result = conn.execute(check_referenced_table)
                ref_info = result.fetchone()
                
                if ref_info and ref_info[2] == 'openai_keys':
                    print("      📋 Dropping old foreign key constraint...")
                    conn.execute(text("""
                        ALTER TABLE agents 
                        DROP CONSTRAINT agents_openai_key_id_fkey
                    """))
                    print("      ✅ Dropped old constraint")
                elif ref_info and ref_info[2] == 'service_account_key':
                    print("      ✅ Constraint already points to service_account_key")
                    return
                else:
                    print(f"      ⚠️  Constraint references unexpected table: {ref_info[2] if ref_info else 'unknown'}")
            
            # Add the new foreign key constraint
            print("      📋 Adding new foreign key constraint...")
            conn.execute(text("""
                ALTER TABLE agents 
                ADD CONSTRAINT agents_openai_key_id_fkey 
                FOREIGN KEY (openai_key_id) 
                REFERENCES service_account_key(id)
            """))
            print("      ✅ Added new constraint")
            
        except Exception as e:
            error_msg = str(e)
            if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                print("      ⏭️  Constraint already exists (skipping)")
            elif "does not exist" in error_msg.lower():
                print("      ⏭️  Constraint doesn't exist (will be created by SQLAlchemy)")
            else:
                print(f"      ⚠️  Migration warning: {e}")
                # Don't exit, just warn - SQLAlchemy will create it correctly on next run

if __name__ == "__main__":
    migrate_agent_foreign_key()


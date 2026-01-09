"""
Migration script to add password_set column and make hashed_password nullable
"""
import sys
from sqlalchemy import create_engine, text, inspect
from app.core.database import engine, Base
from app.core.config import settings

def add_user_columns():
    """Add password_set column and make hashed_password nullable"""
    
    # Check database type
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    is_sqlite = db_url.startswith('sqlite://')
    
    with engine.connect() as conn:
        if is_postgres:
            # PostgreSQL
            print("[Migration] Detected PostgreSQL database")
            
            # Check if password_set column exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='password_set'
            """)
            result = conn.execute(check_query)
            has_password_set = result.fetchone() is not None
            
            # Check if hashed_password is nullable
            check_nullable = text("""
                SELECT is_nullable 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='hashed_password'
            """)
            result = conn.execute(check_nullable)
            nullable_result = result.fetchone()
            is_nullable = nullable_result[0] == 'YES' if nullable_result else False
            
            # Add password_set column if it doesn't exist
            if not has_password_set:
                print("[Migration] Adding password_set column...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN password_set BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                print("[Migration] ✓ Added password_set column")
            else:
                print("[Migration] ✓ password_set column already exists")
            
            # Make hashed_password nullable if it's not already
            if not is_nullable:
                print("[Migration] Making hashed_password nullable...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ALTER COLUMN hashed_password DROP NOT NULL
                """))
                conn.commit()
                print("[Migration] ✓ Made hashed_password nullable")
            else:
                print("[Migration] ✓ hashed_password is already nullable")
            
            # Update existing users to have password_set = True if they have a password
            print("[Migration] Updating existing users...")
            conn.execute(text("""
                UPDATE users 
                SET password_set = TRUE 
                WHERE hashed_password IS NOT NULL
            """))
            conn.commit()
            print("[Migration] ✓ Updated existing users")
            
        elif is_sqlite:
            # SQLite - more complex, need to recreate table
            print("[Migration] Detected SQLite database")
            print("[Migration] SQLite doesn't support ALTER COLUMN easily.")
            print("[Migration] Creating new table with updated schema...")
            
            # Check if password_set column exists
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'password_set' not in columns:
                # SQLite workaround: Create new table, copy data, drop old, rename
                conn.execute(text("""
                    CREATE TABLE users_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email VARCHAR NOT NULL UNIQUE,
                        username VARCHAR NOT NULL UNIQUE,
                        hashed_password VARCHAR,
                        role VARCHAR NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        password_set BOOLEAN DEFAULT FALSE,
                        created_at DATETIME,
                        updated_at DATETIME
                    )
                """))
                
                # Copy data
                conn.execute(text("""
                    INSERT INTO users_new 
                    (id, email, username, hashed_password, role, is_active, created_at, updated_at, password_set)
                    SELECT 
                        id, email, username, hashed_password, role, is_active, created_at, updated_at,
                        CASE WHEN hashed_password IS NOT NULL THEN 1 ELSE 0 END as password_set
                    FROM users
                """))
                
                # Drop old table and rename
                conn.execute(text("DROP TABLE users"))
                conn.execute(text("ALTER TABLE users_new RENAME TO users"))
                
                # Recreate indexes
                conn.execute(text("CREATE UNIQUE INDEX ix_users_email ON users(email)"))
                conn.execute(text("CREATE UNIQUE INDEX ix_users_username ON users(username)"))
                conn.execute(text("CREATE INDEX ix_users_id ON users(id)"))
                
                conn.commit()
                print("[Migration] ✓ SQLite migration completed")
            else:
                print("[Migration] ✓ password_set column already exists")
        else:
            print(f"[Migration] Unsupported database type: {db_url}")
            print("[Migration] Please manually add the password_set column and make hashed_password nullable")
            return False
    
    print("[Migration] Migration completed successfully!")
    return True

if __name__ == "__main__":
    try:
        add_user_columns()
    except Exception as e:
        print(f"[Migration] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


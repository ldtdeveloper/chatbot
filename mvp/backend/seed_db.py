"""
Database Seeder
Creates database tables and initializes superadmin user.

Run this script manually after project setup:
    python3 seed_db.py
"""
import sys
from sqlalchemy import text, create_engine
from urllib.parse import urlparse
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.agent import AgentType, NoiseReductionMode
from app.utils.auth import get_password_hash

def create_database_if_not_exists():
    """Create the database if it doesn't exist. Returns True if database exists or was created, False otherwise."""
    from app.config import settings
    
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    if not is_postgres:
        # SQLite doesn't need database creation
        return True
    
    # Parse the database URL to extract components
    # Handle both postgresql:// and postgresql+psycopg2:// formats
    clean_url = db_url.replace('postgresql+psycopg2://', 'postgresql://')
    parsed = urlparse(clean_url)
    db_name = parsed.path.lstrip('/')
    db_user = parsed.username
    db_password = parsed.password
    db_host = parsed.hostname or 'localhost'
    db_port = parsed.port or 5432
    
    if not db_name:
        print("⚠️ No database name found in DATABASE_URL")
        return False
    
    # Connect to default postgres database to create the target database
    default_db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres"
    
    print(f"\n🔍 Checking if database '{db_name}' exists...")
    default_engine = create_engine(default_db_url, isolation_level="AUTOCOMMIT")
    
    try:
        with default_engine.connect() as conn:
            # Check if database exists (using parameterized query for safety)
            check_db = text("SELECT 1 FROM pg_database WHERE datname = :db_name")
            result = conn.execute(check_db, {"db_name": db_name})
            db_exists = result.fetchone() is not None
            
            if not db_exists:
                print(f"   Database '{db_name}' does not exist. Creating...")
                try:
                    # Escape database name properly for PostgreSQL
                    # PostgreSQL identifiers need to be quoted if they contain special characters
                    escaped_db_name = db_name.replace('"', '""')  # Escape double quotes
                    create_db = text(f'CREATE DATABASE "{escaped_db_name}"')
                    conn.execute(create_db)
                    print(f"✅ Database '{db_name}' created successfully!")
                    return True
                except Exception as create_error:
                    error_str = str(create_error)
                    if "permission denied" in error_str.lower() or "insufficientprivilege" in error_str.lower():
                        print(f"\n❌ Permission denied: User '{db_user}' does not have permission to create databases.")
                        print(f"\n📋 Please create the database manually as a PostgreSQL superuser:")
                        print(f"   Option 1: Create the database directly")
                        print(f"   sudo -u postgres psql -c \"CREATE DATABASE {db_name};\"")
                        print(f"\n   Option 2: Grant CREATEDB privilege to the user")
                        print(f"   sudo -u postgres psql -c \"ALTER USER {db_user} CREATEDB;\"")
                        print(f"\n   Option 3: Connect as postgres user and create:")
                        print(f"   psql -U postgres -c \"CREATE DATABASE {db_name};\"")
                        print(f"\n❌ Cannot continue without the database. Exiting...")
                        return False
                    else:
                        # Re-raise other errors
                        raise
            else:
                print(f"✅ Database '{db_name}' already exists")
                return True
    except Exception as e:
        error_str = str(e)
        if "permission denied" in error_str.lower() or "insufficientprivilege" in error_str.lower():
            print(f"\n❌ Permission denied: User '{db_user}' does not have permission to check databases.")
            print(f"❌ Please ensure the database '{db_name}' exists before running this script.")
            print(f"❌ Cannot continue without database access. Exiting...")
            return False
        else:
            print(f"❌ Error checking/creating database: {e}")
            raise
    finally:
        default_engine.dispose()

def create_enum_types():
    """Create PostgreSQL enum types if they don't exist"""
    from app.config import settings
    
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    
    if not is_postgres:
        # SQLite doesn't need enum types
        return
    
    print("\n🔧 Creating PostgreSQL enum types...")
    with engine.connect() as conn:
        try:
            # Create agenttype enum if it doesn't exist
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE agenttype AS ENUM ('WEB', 'PHONE');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            # Create noisereductionmode enum if it doesn't exist
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE noisereductionmode AS ENUM ('near_field', 'far_field');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            conn.commit()
            print("✅ Enum types created successfully!")
        except Exception as e:
            print(f"⚠️ Warning creating enum types (they may already exist): {e}")
            conn.rollback()

def migrate_user_columns():
    """Add missing columns to users table if they don't exist"""
    from app.config import settings
    
    db_url = settings.database_url
    is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
    is_sqlite = db_url.startswith('sqlite://')
    
    print("\n🔧 Checking and migrating user table columns...")
    with engine.connect() as conn:
        try:
            if is_postgres:
                # Check if password_set column exists
                check_query = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='password_set'
                """)
                result = conn.execute(check_query)
                has_password_set = result.fetchone() is not None
                
                # Add password_set column if it doesn't exist
                if not has_password_set:
                    print("   Adding password_set column to users table...")
                    conn.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN password_set BOOLEAN DEFAULT FALSE
                    """))
                    conn.commit()
                    print("✅ Added password_set column")
                else:
                    print("✅ password_set column already exists")
                
                # Check if hashed_password is nullable
                check_nullable = text("""
                    SELECT is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='hashed_password'
                """)
                result = conn.execute(check_nullable)
                nullable_result = result.fetchone()
                is_nullable = nullable_result[0] == 'YES' if nullable_result else False
                
                # Make hashed_password nullable if it's not already
                if not is_nullable:
                    print("   Making hashed_password nullable...")
                    conn.execute(text("""
                        ALTER TABLE users 
                        ALTER COLUMN hashed_password DROP NOT NULL
                    """))
                    conn.commit()
                    print("✅ Made hashed_password nullable")
                else:
                    print("✅ hashed_password is already nullable")
                    
            elif is_sqlite:
                # For SQLite, check if column exists by inspecting table schema
                from sqlalchemy import inspect as sqlalchemy_inspect
                inspector = sqlalchemy_inspect(engine)
                if inspector.has_table('users'):
                    columns = [col['name'] for col in inspector.get_columns('users')]
                    
                    if 'password_set' not in columns:
                        print("   SQLite: Adding password_set column...")
                        # SQLite doesn't support ALTER TABLE ADD COLUMN with DEFAULT easily
                        # We'll need to recreate the table or use a migration
                        print("⚠️ SQLite migration for password_set requires manual table recreation")
                        print("   Consider using PostgreSQL for production or run add_user_columns.py")
                    else:
                        print("✅ password_set column already exists")
                else:
                    print("⚠️ users table doesn't exist yet - will be created with all columns")
            
        except Exception as e:
            print(f"⚠️ Warning during user column migration (columns may already exist): {e}")
            conn.rollback()

def seed_database():
    """Create database tables and seed initial data"""
    print("🌱 Starting database seeding...")
    
    # Step 0: Create database if it doesn't exist
    db_ready = create_database_if_not_exists()
    if not db_ready:
        print("\n❌ Database setup failed. Please create the database manually and try again.")
        sys.exit(1)
    
    # Step 0.5: Create enum types for PostgreSQL
    create_enum_types()
    
    # Step 1: Create all database tables
    print("\n📦 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        sys.exit(1)
    
    # Step 1.5: Migrate user table columns (add missing columns like password_set)
    migrate_user_columns()
    
    # Step 2: Create/Update superadmin user
    print("\n👤 Setting up superadmin user...")
    db = SessionLocal()
    try:
        # Check if superadmin already exists
        existing = db.query(User).filter(User.email == "superadmin@yopmail.com").first()
        
        if existing:
            # Update existing superadmin
            print("   Found existing superadmin user, updating...")
            existing.username = "superadmin"
            existing.hashed_password = get_password_hash("123456")
            existing.role = UserRole.SUPERADMIN
            existing.is_active = True
            db.commit()
            db.refresh(existing)
            print("✅ Superadmin user updated successfully!")
        else:
            # Create new superadmin
            print("   Creating new superadmin user...")
            superadmin = User(
                email="superadmin@yopmail.com",
                username="superadmin",
                hashed_password=get_password_hash("123456"),
                role=UserRole.SUPERADMIN,
                is_active=True,
                password_set = True
            )
            db.add(superadmin)
            db.commit()
            db.refresh(superadmin)
            print("✅ Superadmin user created successfully!")
        
        # Display credentials
        print("\n📋 Superadmin Credentials:")
        print("   Email: superadmin@yopmail.com")
        print("   Username: superadmin")
        print("   Password: 123456")
        print("   Role: superadmin")
        
        print("\n✅ Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()


"""
Database Seeder
Migrates all database schemas and initializes superadmin user.

Note: Database must already exist. This script only migrates schemas and seeds data.

Run this script manually after project setup:
    python3 seed_db.py
"""
import sys
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.config import settings
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.agent import AgentType, NoiseReductionMode
from app.utils.auth import get_password_hash

# Import all models to ensure they're registered with Base.metadata
# This ensures all tables are included in Base.metadata.create_all()
from app.models import (
    OpenAIKey, Agent, AssistantConfig, Interaction,
    IntegrationConfig, UserReportPreference, ReportJob, ReportFrequency, JobStatus,
    Subscription, PlanType, PaymentStatus, PaymentToken, ServiceAccountKey
)


def check_database_connection():
    """Check if database connection is available"""
    print("🔍 Checking database connection...")
    try:
        with engine.connect() as conn:
            # Simple query to test connection
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        return True
    except OperationalError as e:
        print(f"❌ Cannot connect to database: {e}")
        print(f"   Please ensure:")
        print(f"   1. Database exists and is accessible")
        print(f"   2. DATABASE_URL in .env file is correct")
        print(f"   3. Database server is running")
        return False


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
    """Migrate database schemas and seed initial data"""
    print("🌱 Starting database schema migration and seeding...")
    
    # Step 0: Check database connection
    if not check_database_connection():
        print("❌ Database connection failed. Exiting...")
        sys.exit(1)
    
    # Step 1: Create enum types for PostgreSQL
    create_enum_types()
    
    # Step 2: Import all models to ensure they're registered with Base.metadata
    print("\n📚 Registering all database models...")
    try:
        # All models are already imported at the top of the file
        # This ensures Base.metadata includes all tables
        model_count = len(Base.metadata.tables)
        print(f"✅ Registered {model_count} database models")
    except Exception as e:
        print(f"⚠️ Warning registering models: {e}")
    
    # Step 3: Create all database tables (migrate all schemas)
    print("\n📦 Migrating all database schemas...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All database tables created/migrated successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        sys.exit(1)
    
    # Step 4: Migrate user table columns (add missing columns like password_set)
    migrate_user_columns()
    
    # Step 5: Migrate agents table foreign key (from openai_keys to service_account_key)
    print("\n🔗 Migrating agents table foreign key constraint...")
    try:
        # Import here to avoid circular dependencies
        import chatbot.mvp.backend.app.migrations.migrate_agent_foreign_key as migrate_agent_foreign_key
        migrate_agent_foreign_key.migrate_agent_foreign_key()
    except Exception as e:
        print(f"   ⚠️ Warning: Could not migrate agents foreign key: {e}")
        print("   This is OK if the constraint is already correct or table doesn't exist yet")
    
    # Step 6: Migrate interactions table foreign key (from openai_keys to service_account_key)
    print("\n🔗 Migrating interactions table foreign key constraint...")
    try:
        db_url = settings.database_url
        is_postgres = ('postgresql' in db_url or 'postgres' in db_url) and not db_url.startswith('sqlite://')
        
        if is_postgres:
            with engine.begin() as conn:
                # Check if interactions table exists
                check_table = text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'interactions'
                    )
                """)
                result = conn.execute(check_table)
                if result.scalar():
                    # Check what the current constraint references
                    check_constraint = text("""
                        SELECT 
                            tc.constraint_name,
                            ccu.table_name AS foreign_table_name
                        FROM information_schema.table_constraints AS tc
                        JOIN information_schema.key_column_usage AS kcu
                          ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage AS ccu
                          ON ccu.constraint_name = tc.constraint_name
                        WHERE tc.table_name = 'interactions' 
                        AND tc.constraint_type = 'FOREIGN KEY'
                        AND kcu.column_name = 'openai_key_id'
                    """)
                    result = conn.execute(check_constraint)
                    constraint_info = result.fetchone()
                    
                    if constraint_info:
                        constraint_name, foreign_table = constraint_info
                        if foreign_table == 'openai_keys':
                            print(f"   📋 Dropping old interactions foreign key constraint...")
                            conn.execute(text(f"""
                                ALTER TABLE interactions 
                                DROP CONSTRAINT IF EXISTS {constraint_name}
                            """))
                            conn.execute(text("""
                                ALTER TABLE interactions 
                                ADD CONSTRAINT interactions_openai_key_id_fkey 
                                FOREIGN KEY (openai_key_id) 
                                REFERENCES service_account_key(id)
                            """))
                            print("   ✅ Fixed interactions foreign key constraint")
    except Exception as e:
        print(f"   ⚠️ Warning: Could not migrate interactions foreign key: {e}")
        print("   This is OK if the constraint is already correct or table doesn't exist yet")
    
    # Step 7: Create/Update superadmin user
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


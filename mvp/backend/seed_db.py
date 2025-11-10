"""
Database Seeder
Creates database tables and initializes superadmin user.

Run this script manually after project setup:
    python3 seed_db.py
"""
import sys
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.utils.auth import get_password_hash

def seed_database():
    """Create database tables and seed initial data"""
    print("🌱 Starting database seeding...")
    
    # Step 1: Create all database tables
    print("\n📦 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        sys.exit(1)
    
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
                is_active=True
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


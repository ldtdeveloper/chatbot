"""
Script to create superadmin user
Run this once to initialize the superadmin account
"""
import sys
import bcrypt
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def create_superadmin():
    db = SessionLocal()
    try:
        # Check if superadmin already exists
        existing = db.query(User).filter(User.email == "superadmin@yopmail.com").first()
        if existing:
            print("Superadmin user already exists!")
            return
        
        # Create superadmin user
        password = "qwe123QWE!@#"
        # Hash with bcrypt directly
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        hashed_password = hashed.decode('utf-8')
        
        superadmin = User(
            email="superadmin@yopmail.com",
            username="superadmin",
            hashed_password=hashed_password,
            role=UserRole.SUPERADMIN,
            is_active=True
        )
        
        db.add(superadmin)
        db.commit()
        db.refresh(superadmin)
        
        print("✅ Superadmin user created successfully!")
        print(f"   Email: superadmin@yopmail.com")
        print(f"   Password: qwe123QWE!@#")
        print(f"   Role: {superadmin.role.value}")
        
    except Exception as e:
        print(f"❌ Error creating superadmin: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_superadmin()


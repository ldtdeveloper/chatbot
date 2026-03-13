import sys
import os
sys.path.append(os.getcwd())

from app.core.database import engine, SessionLocal
from app.models.user_company import UserCompany
from app.models.company import Company
from app.models.user import User

def setup():
    # Create the table
    print("Creating user_company_mappings table...")
    UserCompany.__table__.create(bind=engine, checkfirst=True)
    
    db = SessionLocal()
    try:
        # Find user 59 (david@yopmail.com)
        user = db.query(User).filter(User.email == "david@yopmail.com").first()
        if not user:
            print("User david@yopmail.com not found.")
            return

        # Find first company
        company = db.query(Company).first()
        if not company:
            print("No company found to map.")
            return

        # Check if mapping already exists
        existing = db.query(UserCompany).filter(
            UserCompany.user_id == user.id,
            UserCompany.company_id == company.id
        ).first()

        if existing:
            print(f"Mapping already exists: User {user.id} -> Company {company.id}")
        else:
            mapping = UserCompany(user_id=user.id, company_id=company.id)
            db.add(mapping)
            db.commit()
            print(f"Created mapping: User {user.id} ({user.email}) -> Company {company.id} ({company.name})")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup()

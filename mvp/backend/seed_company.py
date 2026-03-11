"""
One-time seed script to create the initial company in the database.
Run with: python seed_company.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.company import Company

def seed():
    db = SessionLocal()
    try:
        slug = "rachit-technologies"
        existing = db.query(Company).filter(Company.slug == slug).first()
        if existing:
            print(f"✅ Company already exists: '{existing.name}' (slug: {existing.slug})")
            return

        company = Company(name="Rachit Technologies", slug=slug)
        db.add(company)
        db.commit()
        db.refresh(company)
        print(f"✅ Created company: '{company.name}' (id: {company.id}, slug: {company.slug})")
        print(f"\n🔗 Agent login URL: http://localhost:5173/agent-login/{company.slug}")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()

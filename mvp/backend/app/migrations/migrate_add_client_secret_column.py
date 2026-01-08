#!/usr/bin/env python3
"""
Migration script to add oauth_client_secret_encrypted column to integration_config table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text

def migrate():
    """Add oauth_client_secret_encrypted column"""
    print("Starting migration: Adding oauth_client_secret_encrypted column...")
    
    with engine.connect() as conn:
        try:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='integration_config' 
                AND column_name='oauth_client_secret_encrypted'
            """))
            
            if result.fetchone():
                print("✅ Column oauth_client_secret_encrypted already exists. Skipping migration.")
                return
            
            # Add the column
            conn.execute(text("""
                ALTER TABLE integration_config 
                ADD COLUMN oauth_client_secret_encrypted VARCHAR
            """))
            conn.commit()
            print("✅ Successfully added oauth_client_secret_encrypted column")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()


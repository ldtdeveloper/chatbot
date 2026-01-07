"""
Migration: Add OAuth columns to integration_config table
========================================================
Adds OAuth-related columns for HubSpot OAuth integration

Run: python migrate_oauth_columns.py
"""
from sqlalchemy import create_engine, text
from app.config import settings

# Create engine
engine = create_engine(settings.database_url)


def add_columns():
    """Add OAuth columns to integration_config table"""
    
    # OAuth columns to add
    oauth_columns = [
        ("oauth_access_token", "VARCHAR"),
        ("oauth_refresh_token", "VARCHAR"),
        ("oauth_client_id", "VARCHAR"),
        ("oauth_token_expires_at", "TIMESTAMP WITH TIME ZONE"),
        ("oauth_installed_at", "TIMESTAMP WITH TIME ZONE"),
        ("oauth_install_url", "VARCHAR"),
    ]
    
    print("📦 Adding OAuth columns to integration_config table...")
    print("-" * 50)
    
    with engine.connect() as conn:
        for col_name, col_type in oauth_columns:
            try:
                # Check if column exists first
                if 'postgresql' in settings.database_url:
                    check_sql = text(f"""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = 'integration_config' AND column_name = '{col_name}'
                    """)
                else:
                    # SQLite
                    check_sql = text(f"PRAGMA table_info(integration_config)")
                
                result = conn.execute(check_sql)
                
                # For SQLite, check if column exists in results
                if 'sqlite' in settings.database_url:
                    columns = [row[1] for row in result.fetchall()]
                    if col_name in columns:
                        print(f"   ⏭️  {col_name} already exists")
                        continue
                else:
                    # PostgreSQL
                    if result.fetchone():
                        print(f"   ⏭️  {col_name} already exists")
                        continue
                
                # Add the column
                if 'postgresql' in settings.database_url:
                    alter_sql = text(f"ALTER TABLE integration_config ADD COLUMN {col_name} {col_type}")
                else:
                    # SQLite doesn't support TIMESTAMP WITH TIME ZONE, use TIMESTAMP
                    sqlite_type = "TIMESTAMP" if "TIMESTAMP" in col_type else col_type
                    alter_sql = text(f"ALTER TABLE integration_config ADD COLUMN {col_name} {sqlite_type}")
                
                conn.execute(alter_sql)
                conn.commit()
                print(f"   ✅ Added {col_name}")
                
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"   ⏭️  {col_name} already exists")
                else:
                    print(f"   ❌ Error adding {col_name}: {e}")
        
        # Make encrypted_key nullable if it's not already
        try:
            if 'postgresql' in settings.database_url:
                # Check if encrypted_key is nullable
                check_nullable = text("""
                    SELECT is_nullable FROM information_schema.columns 
                    WHERE table_name = 'integration_config' AND column_name = 'encrypted_key'
                """)
                result = conn.execute(check_nullable)
                row = result.fetchone()
                if row and row[0] == 'NO':
                    alter_sql = text("ALTER TABLE integration_config ALTER COLUMN encrypted_key DROP NOT NULL")
                    conn.execute(alter_sql)
                    conn.commit()
                    print(f"   ✅ Made encrypted_key nullable")
                else:
                    print(f"   ⏭️  encrypted_key is already nullable")
        except Exception as e:
            print(f"   ⚠️  Could not modify encrypted_key: {e}")
    
    print("-" * 50)
    print("✅ Migration complete!")


def verify_columns():
    """Verify all OAuth columns exist"""
    print("\n📋 Verifying OAuth columns...")
    
    expected_columns = [
        "oauth_access_token",
        "oauth_refresh_token", 
        "oauth_client_id",
        "oauth_token_expires_at",
        "oauth_installed_at",
        "oauth_install_url"
    ]
    
    with engine.connect() as conn:
        if 'postgresql' in settings.database_url:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'integration_config'
                ORDER BY ordinal_position
            """))
            existing_columns = [row[0] for row in result.fetchall()]
        else:
            result = conn.execute(text("PRAGMA table_info(integration_config)"))
            existing_columns = [row[1] for row in result.fetchall()]
        
        print("\nOAuth columns status:")
        for col in expected_columns:
            if col in existing_columns:
                print(f"   ✅ {col}")
            else:
                print(f"   ❌ {col} - MISSING")


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 OAuth Columns Migration")
    print("=" * 60)
    
    add_columns()
    verify_columns()
    
    print("\n✅ Done! OAuth columns have been added to integration_config table.")


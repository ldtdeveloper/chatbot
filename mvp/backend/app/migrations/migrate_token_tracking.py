"""
Migration: Add detailed token tracking columns to interactions table
====================================================================
Adds columns for real OpenAI token-based cost tracking

Run: python migrate_token_tracking.py
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

# Create engine
engine = create_engine(settings.database_url)


def add_columns():
    """Add new token tracking columns to interactions table"""
    
    # New columns to add
    new_columns = [
        # Audio tokens
        ("audio_input_tokens", "INTEGER DEFAULT 0"),
        ("audio_output_tokens", "INTEGER DEFAULT 0"),
        # Text tokens
        ("text_input_tokens", "INTEGER DEFAULT 0"),
        ("text_output_tokens", "INTEGER DEFAULT 0"),
        # Cost breakdown
        ("audio_input_cost", "FLOAT DEFAULT 0.0"),
        ("audio_output_cost", "FLOAT DEFAULT 0.0"),
        ("text_input_cost", "FLOAT DEFAULT 0.0"),
        ("text_output_cost", "FLOAT DEFAULT 0.0"),
    ]
    
    print("📦 Adding token tracking columns to interactions table...")
    print("-" * 50)
    
    with engine.connect() as conn:
        for col_name, col_type in new_columns:
            try:
                # Check if column exists first
                if 'postgresql' in settings.database_url:
                    check_sql = text(f"""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = 'interactions' AND column_name = '{col_name}'
                    """)
                else:
                    # SQLite
                    check_sql = text(f"PRAGMA table_info(interactions)")
                
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
                alter_sql = text(f"ALTER TABLE interactions ADD COLUMN {col_name} {col_type}")
                conn.execute(alter_sql)
                conn.commit()
                print(f"   ✅ Added {col_name}")
                
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"   ⏭️  {col_name} already exists")
                else:
                    print(f"   ❌ Error adding {col_name}: {e}")
    
    print("-" * 50)
    print("✅ Migration complete!")


def verify_columns():
    """Verify all columns exist"""
    print("\n📋 Verifying columns...")
    
    with engine.connect() as conn:
        if 'postgresql' in settings.database_url:
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'interactions'
                ORDER BY ordinal_position
            """))
        else:
            result = conn.execute(text("PRAGMA table_info(interactions)"))
        
        print("\nInteractions table columns:")
        for row in result.fetchall():
            if 'postgresql' in settings.database_url:
                print(f"   - {row[0]}: {row[1]}")
            else:
                print(f"   - {row[1]}: {row[2]}")


def show_pricing():
    """Show current OpenAI pricing"""
    print("\n💰 OpenAI Realtime API Pricing (Dec 2024):")
    print("-" * 50)
    print("   Audio Input:  $0.10 / 1K tokens")
    print("   Audio Output: $0.20 / 1K tokens")
    print("   Text Input:   $0.005 / 1K tokens")
    print("   Text Output:  $0.02 / 1K tokens")
    print("-" * 50)
    print("\n📊 Example cost calculation:")
    print("   1000 audio input + 500 audio output + 100 text")
    print("   = $0.10 + $0.10 + ~$0.002 = $0.202")


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Token Tracking Migration")
    print("=" * 60)
    
    add_columns()
    verify_columns()
    show_pricing()
    
    print("\n✅ Done! Restart the backend to use real token-based cost tracking.")


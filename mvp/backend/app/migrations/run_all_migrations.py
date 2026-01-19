"""
Run all database migrations in the correct order

Usage:
    cd mvp/backend
    python -m app.migrations.run_all_migrations
    OR
    python app/migrations/run_all_migrations.py
"""
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.core.config import settings
from app.core.database import SessionLocal

def run_migrations():
    """Run all migrations in the correct order"""
    print("=" * 80)
    print("DATABASE MIGRATION RUNNER")
    print("=" * 80)
    print(f"Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else settings.database_url}")
    print("=" * 80)
    
    # List of migrations in order (dependencies first)
    migrations = [
        # Core migrations
        ("add_user_columns", "Add user columns (password_set, etc.)"),
        ("migrate_agent_foreign_key", "Migrate agents foreign key"),
        ("migrate_interactions", "Migrate interactions table"),
        ("migrate_prompts_to_agents", "Migrate prompts to agents"),
        ("migrate_reports", "Migrate reports tables"),
        ("migrate_token_tracking", "Migrate token tracking"),
        ("migrate_add_client_secret_column", "Add client_secret column"),
        
        # Wallet-related migrations (in order)
        ("migrate_add_wallet_balance", "Add wallet_balance column (deprecated - use migrate_to_wallet_model)"),
        ("migrate_to_wallet_model", "Migrate to Wallet model"),
        ("migrate_wallet_and_keys", "Sync wallet and agent keys"),
        ("migrate_wallet_transactions", "Create wallet_transactions table"),
        
        # Cost-related migrations
        ("migrate_add_total_cost", "Add total_cost column to interactions"),
        
        # Agent activation
        ("migrate_agent_is_active", "Add is_active column to agents"),
        
        # Plans schema updates
        ("migrate_plans_schema", "Update plans table schema (currency, plan_type, wallet_credits)"),
    ]
    
    failed_migrations = []
    
    for migration_name, description in migrations:
        print(f"\n{'='*80}")
        print(f"Running: {migration_name}")
        print(f"Description: {description}")
        print(f"{'='*80}")
        
        try:
            # Import the migration module
            module = __import__(f'app.migrations.{migration_name}', fromlist=[migration_name])
            
            # Find the main function (usually migrate() or migrate_*())
            migrate_func = None
            for attr_name in dir(module):
                if attr_name.startswith('migrate') and callable(getattr(module, attr_name)):
                    migrate_func = getattr(module, attr_name)
                    break
            
            if not migrate_func:
                # Try common function names
                if hasattr(module, 'migrate'):
                    migrate_func = module.migrate
                elif hasattr(module, f'migrate_{migration_name}'):
                    migrate_func = getattr(module, f'migrate_{migration_name}')
                else:
                    print(f"⚠️  No migration function found in {migration_name}")
                    failed_migrations.append((migration_name, "No migration function found"))
                    continue
            
            # Run the migration
            migrate_func()
            print(f"✅ {migration_name} completed successfully")
            
        except Exception as e:
            print(f"❌ {migration_name} failed: {e}")
            import traceback
            traceback.print_exc()
            failed_migrations.append((migration_name, str(e)))
            # Ask if user wants to continue
            response = input(f"\n⚠️  Migration {migration_name} failed. Continue with next migration? (y/n): ")
            if response.lower() != 'y':
                print("\n❌ Migration process stopped by user")
                break
    
    # Summary
    print("\n" + "=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    
    if failed_migrations:
        print(f"\n❌ {len(failed_migrations)} migration(s) failed:")
        for migration_name, error in failed_migrations:
            print(f"   - {migration_name}: {error}")
        print("\n⚠️  Please review the errors above and fix them before proceeding.")
        return False
    else:
        print("\n✅ All migrations completed successfully!")
        return True

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)

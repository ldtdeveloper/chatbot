"""
Migration script to convert Prompts to Agents
This script:
1. Creates the new 'agents' table
2. Migrates data from 'prompts' and 'prompt_versions' to 'agents'
3. Updates 'assistant_configs' to use 'agent_id' instead of 'prompt_id' and 'prompt_version_id'
4. Drops old 'prompts' and 'prompt_versions' tables
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = './voice_assistant.db'

def migrate():
    if not os.path.exists(DB_PATH):
        print("Database does not exist. Tables will be created automatically on first run.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("Starting migration from Prompts to Agents...")
        
        # Check if agents table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agents'")
        agents_exists = cursor.fetchone() is not None
        
        if agents_exists:
            print("⚠️  'agents' table already exists.")
            # Check if we still need to migrate data
            cursor.execute("SELECT COUNT(*) FROM agents")
            agents_count = cursor.fetchone()[0]
            print(f"   Current agents count: {agents_count}")
            
            # Check if prompts table still exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prompts'")
            prompts_exists = cursor.fetchone() is not None
            
            if not prompts_exists:
                print("✅ Migration already completed (prompts table removed).")
                # Just need to update assistant_configs if needed
                cursor.execute("PRAGMA table_info(assistant_configs)")
                columns = [col[1] for col in cursor.fetchall()]
                if 'agent_id' in columns and 'prompt_id' in columns:
                    print("Updating assistant_configs to remove prompt_id...")
                    # Will handle this below
                else:
                    print("✅ assistant_configs already updated.")
                    conn.close()
                    return
            else:
                print("⚠️  Both tables exist. Will migrate data and clean up.")
        else:
            prompts_exists = True
            # Create agents table if it doesn't exist
            print("Creating 'agents' table...")
            cursor.execute("""
                CREATE TABLE agents (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    openai_key_id INTEGER NOT NULL,
                    name VARCHAR NOT NULL,
                    description TEXT,
                    instructions TEXT NOT NULL,
                    voice VARCHAR DEFAULT 'alloy',
                    noise_reduction_mode VARCHAR DEFAULT 'near_field',
                    noise_reduction_threshold VARCHAR DEFAULT '0.5',
                    noise_reduction_prefix_padding_ms INTEGER DEFAULT 300,
                    noise_reduction_silence_duration_ms INTEGER DEFAULT 500,
                    agent_config TEXT DEFAULT '{}',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME,
                    FOREIGN KEY(user_id) REFERENCES users (id),
                    FOREIGN KEY(openai_key_id) REFERENCES openai_keys (id)
                )
            """)
            
            # Create index on user_id
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_agents_user_id ON agents(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_agents_openai_key_id ON agents(openai_key_id)")
        
        # Migrate data from prompts/prompt_versions to agents
        if prompts_exists:
            print("Migrating data from 'prompts' and 'prompt_versions' to 'agents'...")
            
            # Get all prompts with their latest versions
            # Note: prompt_versions may not have all noise reduction fields
            cursor.execute("""
                SELECT 
                    p.id,
                    p.user_id,
                    COALESCE(p.openai_key_id, 1) as openai_key_id,
                    p.name,
                    p.description,
                    pv.system_instructions,
                    pv.voice,
                    pv.noise_reduction_mode,
                    p.created_at
                FROM prompts p
                LEFT JOIN prompt_versions pv ON p.id = pv.prompt_id AND (pv.is_active = 1 OR pv.id = (
                    SELECT id FROM prompt_versions 
                    WHERE prompt_id = p.id 
                    ORDER BY version_number DESC 
                    LIMIT 1
                ))
                ORDER BY p.id, pv.version_number DESC
            """)
            
            prompts_data = cursor.fetchall()
            
            # Group by prompt id to get the latest version
            seen_prompts = {}
            for row in prompts_data:
                prompt_id = row[0]
                if prompt_id not in seen_prompts:
                    seen_prompts[prompt_id] = row
            
            migrated_count = 0
            for row in seen_prompts.values():
                (prompt_id, user_id, openai_key_id, name, description, 
                 instructions, voice, noise_reduction_mode, created_at) = row
                
                # Use default values if version data is missing
                if instructions is None:
                    instructions = description or f"Agent: {name}"
                if voice is None:
                    voice = "alloy"
                if noise_reduction_mode is None:
                    noise_reduction_mode = "near_field"
                # These fields don't exist in prompt_versions, use defaults
                noise_reduction_threshold = "0.5"
                noise_reduction_prefix_padding_ms = 300
                noise_reduction_silence_duration_ms = 500
                
                cursor.execute("""
                    INSERT INTO agents (
                        user_id, openai_key_id, name, description, instructions,
                        voice, noise_reduction_mode, noise_reduction_threshold,
                        noise_reduction_prefix_padding_ms, noise_reduction_silence_duration_ms,
                        agent_config, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, openai_key_id, name, description, instructions,
                    voice, noise_reduction_mode, noise_reduction_threshold,
                    noise_reduction_prefix_padding_ms, noise_reduction_silence_duration_ms,
                    '{}', created_at
                ))
                migrated_count += 1
            
            print(f"✅ Migrated {migrated_count} prompts to agents")
        
        # Update assistant_configs table
        print("Updating 'assistant_configs' table...")
        
        # Check if agent_id column exists
        cursor.execute("PRAGMA table_info(assistant_configs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'agent_id' not in columns:
            # Add agent_id column
            cursor.execute("ALTER TABLE assistant_configs ADD COLUMN agent_id INTEGER")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_assistant_configs_agent_id ON assistant_configs(agent_id)")
            
            # Migrate prompt_id to agent_id if prompts existed
            if prompts_exists:
                print("Migrating prompt_id to agent_id in assistant_configs...")
                # Create a mapping from old prompt_id to new agent_id
                cursor.execute("""
                    SELECT p.id, a.id 
                    FROM prompts p
                    INNER JOIN agents a ON a.user_id = p.user_id 
                        AND a.name = p.name 
                        AND a.openai_key_id = p.openai_key_id
                    ORDER BY p.id, a.id
                """)
                prompt_to_agent = {}
                for old_prompt_id, new_agent_id in cursor.fetchall():
                    if old_prompt_id not in prompt_to_agent:
                        prompt_to_agent[old_prompt_id] = new_agent_id
                
                # Update assistant_configs
                for old_prompt_id, new_agent_id in prompt_to_agent.items():
                    cursor.execute("""
                        UPDATE assistant_configs 
                        SET agent_id = ? 
                        WHERE prompt_id = ?
                    """, (new_agent_id, old_prompt_id))
                
                updated_count = cursor.rowcount
                print(f"✅ Updated {updated_count} assistant_configs records")
        
        # Remove old foreign key constraints and columns if they exist
        if 'prompt_id' in columns:
            print("Removing old 'prompt_id' column from assistant_configs...")
            # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
            cursor.execute("""
                CREATE TABLE assistant_configs_new (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name VARCHAR NOT NULL,
                    agent_id INTEGER,
                    voice VARCHAR DEFAULT 'alloy',
                    noise_reduction_mode VARCHAR DEFAULT 'near_field',
                    noise_reduction_threshold VARCHAR DEFAULT '0.5',
                    noise_reduction_prefix_padding_ms INTEGER DEFAULT 300,
                    noise_reduction_silence_duration_ms INTEGER DEFAULT 500,
                    additional_settings TEXT DEFAULT '{}',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME,
                    FOREIGN KEY(user_id) REFERENCES users (id),
                    FOREIGN KEY(agent_id) REFERENCES agents (id)
                )
            """)
            
            # Copy data (excluding prompt_id and prompt_version_id)
            cursor.execute("""
                INSERT INTO assistant_configs_new (
                    id, user_id, name, agent_id, voice, noise_reduction_mode,
                    noise_reduction_threshold, noise_reduction_prefix_padding_ms,
                    noise_reduction_silence_duration_ms, additional_settings,
                    created_at, updated_at
                )
                SELECT 
                    id, user_id, name, agent_id, voice, noise_reduction_mode,
                    noise_reduction_threshold, noise_reduction_prefix_padding_ms,
                    noise_reduction_silence_duration_ms, additional_settings,
                    created_at, updated_at
                FROM assistant_configs
            """)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE assistant_configs")
            cursor.execute("ALTER TABLE assistant_configs_new RENAME TO assistant_configs")
            
            # Recreate indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_assistant_configs_user_id ON assistant_configs(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_assistant_configs_agent_id ON assistant_configs(agent_id)")
            
            print("✅ Recreated assistant_configs table without prompt_id/prompt_version_id")
        
        # Drop old tables
        if prompts_exists:
            print("Dropping old 'prompt_versions' table...")
            cursor.execute("DROP TABLE IF EXISTS prompt_versions")
            
            print("Dropping old 'prompts' table...")
            cursor.execute("DROP TABLE IF EXISTS prompts")
            
            print("✅ Dropped old prompt tables")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()


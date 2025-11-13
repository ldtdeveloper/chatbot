# backend/agents.py
import os
import sqlite3
import json

# Absolute path to voice_assistant.db
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'voice_assistant.db'))

def get_agent(agent_id: int):
    """
    Fetch agent by id from the voice_assistant.db.
    Returns None if not found, else a dict with keys from DB columns.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    columns = [col[0] for col in cursor.description]
    agent = dict(zip(columns, row))

    # Parse JSON agent_config if present
    if agent.get("agent_config"):
        try:
            agent["agent_config"] = json.loads(agent["agent_config"])
        except Exception:
            agent["agent_config"] = {}
    else:
        agent["agent_config"] = {}

    conn.close()
    return agent


if __name__ == "__main__":
    import sys
    aid = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    print(json.dumps(get_agent(aid), indent=2))

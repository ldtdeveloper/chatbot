import os
from datetime import datetime
from pathlib import Path
from app.core.config import settings

# Directory for conversation logs
LOG_DIR = Path("app/logs/conversations")
LOG_DIR.mkdir(parents=True, exist_ok=True)

def log_message(conversation_id: int, sender: str, content: str):
    """
    Append a message to a conversation log file.
    
    Args:
        conversation_id: ID of the conversation
        sender: Who sent the message (e.g., "User", "AI", "Agent: [Name]")
        content: The message text
    """
    log_file = LOG_DIR / f"{conversation_id}.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"[{timestamp}] {sender}: {content}\n"
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error logging message for conversation {conversation_id}: {e}")

def get_log_path(conversation_id: int) -> Path:
    """Returns the path to a conversation log file."""
    return LOG_DIR / f"{conversation_id}.txt"

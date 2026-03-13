from app.core.database import SessionLocal, engine
from app.models.conversation import Conversation
from app.models.text_agents import TextAgent
from sqlalchemy import or_

db = SessionLocal()
try:
    owner_id = 111
    agent_id = 8
    
    query = (
        db.query(Conversation)
        .join(TextAgent, Conversation.text_agent_id == TextAgent.id)
        .filter(
            Conversation.is_human_active == True,
            TextAgent.user_id == owner_id,
            or_(
                Conversation.human_agent_id == None,
                Conversation.human_agent_id == agent_id
            )
        )
    )
    
    # Print the compiled SQL
    from sqlalchemy.dialects import postgresql
    compiled = query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
    print("--- COMPILED SQL ---")
    print(compiled)
    
    # Run and print count
    results = query.all()
    print(f"\n--- Results: {len(results)} ---")
    
finally:
    db.close()

from app.models.chat_user import ChatUser
from app.models.message import Message
from datetime import datetime
from sqlalchemy.orm import Session

async def process_incoming_message(
    whatsapp_number: str,
    text: str,
    db: Session,
    ai_function,
    send_whatsapp_function,
    broadcast_function
):
    user = db.query(ChatUser).filter(
        ChatUser.whatsapp_number == whatsapp_number
    ).first()

    if not user:
        user = ChatUser(whatsapp_number=whatsapp_number)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Save user message
    db.add(Message(user_id=user.id, content=text, is_from_user=True))
    db.commit()

    # If human is active → send to dashboard only
    if user.is_human_active:
        await broadcast_function({
            "type": "new_message",
            "whatsapp_number": whatsapp_number,
            "content": text,
            "timestamp": datetime.now().isoformat()
        })
        return

    # If trigger words
    if check_handoff_triggers(text):
        user.is_human_active = True
        db.commit()

        await send_whatsapp_function(
            whatsapp_number,
            "I'm connecting you with a human agent. Please hold on 🤝"
        )

        await broadcast_function({
            "type": "handoff_alert",
            "whatsapp_number": whatsapp_number
        })
        return

    # Otherwise → AI
    ai_reply = await ai_function(text)

    await send_whatsapp_function(whatsapp_number, ai_reply)

    db.add(Message(user_id=user.id, content=ai_reply, is_from_user=False))
    db.commit()
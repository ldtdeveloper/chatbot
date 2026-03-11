from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.human_agent import HumanAgent
from app.routes.human_agent_auth import get_current_agent
from app.models.text_agents import TextAgent
from datetime import datetime
import json
from typing import List, Dict
from app.utils.whatsapp_utils import send_whatsapp_message
from app.core.database import SessionLocal
from app.models.message import Message
from app.utils.conversation_logger import log_message, get_log_path
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/handoff", tags=["handoff"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, agent_id: str = "broadcast"):
        await websocket.accept()
        if agent_id not in self.active_connections:
            self.active_connections[agent_id] = []
        self.active_connections[agent_id].append(websocket)

    def disconnect(self, websocket: WebSocket, agent_id: str = "broadcast"):
        if agent_id in self.active_connections:
            self.active_connections[agent_id].remove(websocket)

    async def broadcast(self, message: dict, agent_id: str = "broadcast"):
        if agent_id in self.active_connections:
            # Create a copy of the list to avoid issues if items are removed during iteration
            for connection in list(self.active_connections[agent_id]):
                try:
                    await connection.send_json(message)
                except Exception:
                    # If sending fails, the connection might be dead
                    if connection in self.active_connections[agent_id]:
                        self.active_connections[agent_id].remove(connection)

manager = ConnectionManager()

@router.websocket("/ws/dashboard/{owner_id}")
async def handoff_websocket(websocket: WebSocket, owner_id: str):
    print(f"[WS] Attempting connection for owner_id: {owner_id}")
    await manager.connect(websocket, agent_id=owner_id)
    print(f"[WS] Connected: owner_id={owner_id}")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif message.get("type") == "claim":
                # 1. Update DB first to ensure atomicity 
                whatsapp_number = message.get("whatsapp_number")
                agent_name = message.get("agent_name")
                convo_id = message.get("conversation_id")
                agent_id = message.get("agent_id") # frontend should send this

                db = SessionLocal()
                try:
                    convo = db.query(Conversation).filter(Conversation.id == convo_id).first()
                    if convo:
                        if convo.is_human_active and convo.human_agent_id and convo.human_agent_id != agent_id:
                            # Already claimed by another agent! 
                            await websocket.send_json({
                                "type": "error",
                                "message": f"This chat is already being handled by {convo.human_agent.name if convo.human_agent else 'another agent'}."
                            })
                        else:
                            # Proceed with claim or re-confirmation
                            convo.is_human_active = True
                            convo.human_agent_id = agent_id
                            db.commit()

                            # 2. Broadcast agent_assigned to OTHERS
                            await manager.broadcast({
                                "type": "agent_assigned",
                                "whatsapp_number": whatsapp_number,
                                "agent_name": agent_name,
                                "agent_id": agent_id,  # ADDED: Send claiming agent ID so others can filter
                                "conversation_id": convo_id
                            }, agent_id=str(owner_id))

                            # Note: WhatsApp notification is now handled by the POST takeover endpoint
                except Exception as e:
                    print(f"[WS Claim Error Logic] {e}")
                finally:
                    db.close()
            
            elif message.get("type") == "message":
                # Route message to WhatsApp
                recipient = message.get("to")
                text = message.get("text")
                convo_id = message.get("conversation_id")

                db = SessionLocal()
                try:
                    convo = db.query(Conversation).filter(Conversation.id == convo_id).first()
                    if convo:
                        # 1. Send to WhatsApp
                        success = await send_whatsapp_message(db, convo.text_agent_id, recipient, text)
                        
                        # 2. Save to DB
                        if success:
                            db_msg = Message(
                                conversation_id=convo_id,
                                content=text,
                                is_from_contact=False,
                                is_from_agent=True
                            )
                            db.add(db_msg)
                            db.commit()
                            
                            # 3. Log to file
                            log_message(convo_id, f"Agent: {convo.human_agent.name if (convo and convo.human_agent) else 'Agent'}", text)

                            # 4. Broadcast to other dashboard instances for the SAME owner
                            await manager.broadcast({
                                "type": "new_message",
                                "from": "agent",
                                "whatsapp_number": recipient,
                                "content": text,
                                "conversation_id": convo_id,
                                "timestamp": datetime.utcnow().isoformat()
                            }, agent_id=str(convo.text_agent.user_id))
                finally:
                    db.close()

                print(f"[WS] Message for {recipient}: {text}")
                
    except WebSocketDisconnect:
        print(f"[WS] Disconnected: owner_id={owner_id}")
        manager.disconnect(websocket, agent_id=owner_id)
    except Exception as e:
        print(f"[WS] Error for owner_id {owner_id}: {e}")
        manager.disconnect(websocket, agent_id=owner_id)

# ... (existing routes follow)


# =====================================================
# 🔹 GET ALL ACTIVE HUMAN HANDOFF CONVERSATIONS
# =====================================================
@router.get("/active")
def get_active_handoffs(
    db: Session = Depends(get_db),
    current_agent: dict = Depends(get_current_agent)
):
    owner_id = current_agent.get("owner_id")
    print(f"[DEBUG] Fetching active handoffs for owner_id: {owner_id}, current_agent_id: {current_agent['agent_id']}")

    active_conversations = (
        db.query(Conversation)
        .join(TextAgent, Conversation.text_agent_id == TextAgent.id)
        .filter(
            Conversation.is_human_active.is_(True),
            TextAgent.user_id == owner_id,
            (Conversation.human_agent_id.is_(None)) | (Conversation.human_agent_id == current_agent["agent_id"])
        )
        .all()
    )
    print(f"[DEBUG] Found {len(active_conversations)} conversations")

    response = []

    for convo in active_conversations:
        response.append({
            "conversation_id": convo.id,
            "identifier": convo.contact.identifier if convo.contact else None,
            "agent_type": convo.text_agent.channel if convo.text_agent else "whatsapp",
            "assigned_agent_id": convo.human_agent.id if convo.human_agent else None,
            "assigned_agent_name": convo.human_agent.name if convo.human_agent else None,
            "summary": "Manual takeover active",
            "timestamp": datetime.utcnow().isoformat()
        })

    return response


@router.get("/messages/{conversation_id}")
async def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp.asc())
        .all()
    )

    response = []
    for m in messages:
        sender_name = "User" if m.is_from_contact else ("Agent" if m.is_from_agent else "AI")
        response.append({
            "content": m.content,
            "is_from_contact": m.is_from_contact,
            "is_from_agent": m.is_from_agent,
            "sender_name": sender_name,
            "timestamp": m.timestamp.isoformat() if m.timestamp else datetime.utcnow().isoformat()
        })
    return response


# =====================================================
#  ASSIGN CONVERSATION TO HUMAN AGENT
# =====================================================
@router.post("/assign")
def assign_conversation(
    conversation_id: int,
    agent_id: int,
    db: Session = Depends(get_db),
    current_agent: dict = Depends(get_current_agent)
):
    owner_id = current_agent.get("owner_id")

    #  Check if agent exists & active
    agent = db.query(HumanAgent).filter(
        and_(
            HumanAgent.id == agent_id,
            HumanAgent.is_active.is_(True)
        )
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found or inactive")

    #  Check if agent already handling active conversation
    busy_conversation = db.query(Conversation).filter(
        and_(
            Conversation.human_agent_id == agent.id,
            Conversation.is_human_active.is_(True)
        )
    ).first()

    if busy_conversation:
        raise HTTPException(
            status_code=400,
            detail="Agent already handling another active conversation"
        )

    #  Check conversation exists & belongs to user
    conversation = db.query(Conversation).join(TextAgent).filter(
        Conversation.id == conversation_id,
        TextAgent.user_id == owner_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    #  If already assigned
    if conversation.is_human_active:
        raise HTTPException(
            status_code=400,
            detail="Conversation already assigned to a human agent"
        )

    #  Assign agent
    conversation.human_agent_id = agent.id
    conversation.is_human_active = True

    db.commit()
    db.refresh(conversation)

    return {
        "status": "assigned successfully",
        "conversation_id": conversation.id,
        "assigned_agent_id": agent.id,
        "assigned_agent_name": agent.name
    }


# =====================================================
#  OVERTAKE/CLAIM CONVERSATION (Simplified for Dashboard)
# =====================================================
@router.post("/takeover/{conversation_id}")
async def takeover_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_agent: dict = Depends(get_current_agent)
):
    agent_id = current_agent.get("agent_id")
    owner_id = current_agent.get("owner_id")

    # 1. Find conversation
    conversation = db.query(Conversation).join(TextAgent).filter(
        Conversation.id == conversation_id,
        TextAgent.user_id == owner_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 2. Check if already handled by someone else
    if conversation.is_human_active and conversation.human_agent_id and conversation.human_agent_id != agent_id:
        raise HTTPException(
            status_code=400, 
            detail=f"Already handled by {conversation.human_agent.name if conversation.human_agent else 'another agent'}"
        )

    # 3. Assign to current agent
    conversation.human_agent_id = agent_id
    conversation.is_human_active = True
    db.commit()
    db.refresh(conversation)

    # 4. Broadcast to others that it's taken
    await manager.broadcast({
        "type": "agent_assigned",
        "conversation_id": conversation_id,
        "agent_id": agent_id,
        "agent_name": conversation.human_agent.name if conversation.human_agent else "Agent"
    }, agent_id=str(owner_id))

    # 5. Notify the user on WhatsApp
    if conversation.contact and conversation.contact.identifier:
        await send_whatsapp_message(
            db, 
            conversation.text_agent_id, 
            conversation.contact.identifier, 
            f"You are now connected to {conversation.human_agent.name if conversation.human_agent else 'our agent'}. How can I help you? 😊"
        )

    return {
        "id": conversation.id,
        "identifier": conversation.contact.identifier if conversation.contact else None,
        "assigned_agent_id": agent_id,
        "status": "success"
    }


# =====================================================
#  RELEASE CONVERSATION BACK TO AI
# =====================================================
@router.post("/release/{conversation_id}")
async def release_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_agent: dict = Depends(get_current_agent)
):
    owner_id = current_agent.get("owner_id")

    conversation = db.query(Conversation).join(TextAgent).filter(
        Conversation.id == conversation_id,
        TextAgent.user_id == owner_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation.is_human_active:
        raise HTTPException(
            status_code=400,
            detail="Conversation is not under human control"
        )

    # Notify the user on WhatsApp
    if conversation.contact and conversation.contact.identifier:
        await send_whatsapp_message(
            db, 
            conversation.text_agent_id, 
            conversation.contact.identifier, 
            "An agent has handed this conversation back to our AI assistant. I'm back and ready to help! 🤖✨"
        )
    
    conversation.human_agent_id = None
    conversation.is_human_active = False

    db.commit()
    db.refresh(conversation)

    # Broadcast release so other agents see it in their queue again
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(
            manager.broadcast({
                "type": "agent_unassigned", # Or "new_handover" to make it pop up again
                "conversation_id": conversation_id,
                "identifier": conversation.contact.identifier if conversation.contact else None
            }, agent_id=str(owner_id)),
            loop=loop
        )
    except Exception as e:
        print(f"Broadcast error on release: {e}")

    return {
        "status": "released successfully",
        "conversation_id": conversation.id
    }


# =====================================================
#  DOWNLOAD CONVERSATION LOG
# =====================================================
@router.get("/download/{conversation_id}")
async def download_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_agent: dict = Depends(get_current_agent)
):
    owner_id = current_agent.get("owner_id")

    # Security: Ensure conversation belongs to this owner
    convo = db.query(Conversation).join(TextAgent).filter(
        Conversation.id == conversation_id,
        TextAgent.user_id == owner_id
    ).first()

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")

    log_file = get_log_path(conversation_id)
    if not os.path.exists(log_file):
        # Fallback: Create it if it doesn't exist yet from DB history
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.asc())
            .all()
        )
        for m in messages:
            sender = "User" if m.is_from_contact else ("Agent" if m.is_from_agent else "AI")
            log_message(conversation_id, sender, m.content)

    return FileResponse(
        path=log_file,
        filename=f"conversation_{convo.contact.identifier}_{conversation_id}.txt",
        media_type="text/plain"
    )
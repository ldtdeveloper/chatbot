"""
WhatsApp Routes (Final Clean Version)
- text_agents table: basic text agent info (name, channel=whatsapp, instructions)
- whatsapp_configs table: WhatsApp credentials & status (token, phone_number_id, etc.)
- No fields or rows in main agents table for WhatsApp
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import PlainTextResponse,FileResponse,HTMLResponse
from sqlalchemy.orm import Session
import httpx
from app.routes.text_ai import AIChatRequest,generate_ai_chat
import json 
from fastapi import Request,Query
from typing import Optional
from pathlib import Path
from app.models.contact import Contact
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.human_agent import HumanAgent
import logging
from app.utils.slug import generate_dashboard_slug
from datetime import datetime
from app.core.dependencies import get_optional_current_user
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.text_agents import TextAgent
from app.models.whatsapp_configs import WhatsappConfig
from app.models.subscription import Subscription, PaymentStatus, SubscriptionMode
from app.schemas.whatsapp import (
    WhatsappAgentCreatePayload,
    WhatsappConnectRequest,
    WhatsappConnectResponse,
    WhatsappConnectionStatus,
    WhatsappAgentResponse,
    WhatsappAgentUpdatePayload
)
from app.utils.get_subscription_type import get_subscription_type
from app.routes.whatsapp_handoff import manager
from app.utils.conversation_logger import log_message
from app.tasks.hubspot_task import sync_to_hubspot_task

logger = logging.getLogger(__name__)
WIDGET_DIR = Path(__file__).parent.parent / "static" / "js" 
WIDGET_FILE = WIDGET_DIR / "widget.js"

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp","whatsapp-widget"])


# ──────────────────────────────────────────────────────────────
# 1. Create WhatsApp Text Agent (text_agents table)
# ──────────────────────────────────────────────────────────────
@router.post("/agents")
async def create_whatsapp_agent(
    payload: WhatsappAgentCreatePayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Creating WhatsApp text agent for user {current_user.id}: {payload.name}")

    # Subscription & limit check
    subscription_type = get_subscription_type(current_user.id, db)
    if not subscription_type:
        raise HTTPException(status_code=404, detail="No subscription found")

    whatsapp_count = db.query(TextAgent).filter(
        TextAgent.user_id == current_user.id,
        TextAgent.channel == "whatsapp"
    ).count()

    # Agent limit check from Plan
    limit = 1
    if subscription_type and subscription_type.plans:
        limit = subscription_type.plans.number_of_agents
    
    if whatsapp_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"Agent limit reached. Your current plan allows maximum {limit} WhatsApp agents."
        )

    # Get service account ID (assumed already created at registration)
    openai_key_id = current_user.service_account.id if current_user.service_account else None

    # Create TextAgent (basic text agent info)
    db_text_agent = TextAgent(
        user_id=current_user.id,
        openai_key_id=current_user.service_account.id if current_user.service_account else None,
        channel="whatsapp",
        name=payload.name,
        instructions=payload.instructions or "You are a helpful assistant",
        startup_message=payload.startup_message,
        onboarding_mode=payload.onboarding_mode,
        is_active=True
    )

    db.add(db_text_agent)
    db.flush()

    # Create empty WhatsappConfig
    config = WhatsappConfig(
        text_agent_id=db_text_agent.id,
        phone_number=payload.phone_number,  
        phone_number_id=payload.phone_number_id or None,
        status="pending"
    )

    # Generate a secure random dashboard slug
    config.dashboard_slug = generate_dashboard_slug(db_text_agent.name, db_text_agent.id)
    dashboard_url = f"{settings.frontend_base_url}/agent-login/{config.dashboard_slug}" 

    db.add(config)
    db.commit()
    db.refresh(db_text_agent)

    return {
        "status": "success",
        "text_agent_id": db_text_agent.id,
        "config_id": config.id,
        "name": db_text_agent.name,
        "onboarding_mode": db_text_agent.onboarding_mode,
        "dashboard_url": dashboard_url,
        "message": "WhatsApp text agent created, now connect."
    }


# ──────────────────────────────────────────────────────────────
# 1a. List WhatsApp Agents
# ──────────────────────────────────────────────────────────────
@router.get("/agents", response_model=list[WhatsappAgentResponse])
async def list_whatsapp_agents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agents = db.query(TextAgent).filter(
        TextAgent.user_id == current_user.id,
        TextAgent.channel == "whatsapp"
    ).all()

    result = []
    for agent in agents:
        config = agent.whatsapp_config
        result.append(WhatsappAgentResponse(
            id=agent.id,
            name=agent.name,
            channel=agent.channel,
            instructions=agent.instructions,
            startup_message=agent.startup_message,
            onboarding_mode=agent.onboarding_mode,
            is_active=agent.is_active,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            phone_number=config.phone_number if config else None,
            phone_number_id=config.phone_number_id if config else None,
            status=config.status if config else "not_connected",
            dashboard_slug=config.dashboard_slug if config else None
        ))
    
    return result


# ──────────────────────────────────────────────────────────────
# 1b. Get WhatsApp Agent Details
# ──────────────────────────────────────────────────────────────
@router.get("/agents/{agent_id}", response_model=WhatsappAgentResponse)
async def get_whatsapp_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = db.query(TextAgent).filter(
        TextAgent.id == agent_id,
        TextAgent.user_id == current_user.id,
        TextAgent.channel == "whatsapp"
    ).first()

    if not agent:
        raise HTTPException(404, "WhatsApp agent not found")

    config = agent.whatsapp_config
    return WhatsappAgentResponse(
        id=agent.id,
        name=agent.name,
        channel=agent.channel,
        instructions=agent.instructions,
        startup_message=agent.startup_message,
        onboarding_mode=agent.onboarding_mode,
        is_active=agent.is_active,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
        phone_number=config.phone_number if config else None,
        phone_number_id=config.phone_number_id if config else None,
        status=config.status if config else "not_connected",
        dashboard_slug=config.dashboard_slug if config else None
    )


# ──────────────────────────────────────────────────────────────
# 1c. Update WhatsApp Agent
# ──────────────────────────────────────────────────────────────
@router.put("/agents/{agent_id}")
async def update_whatsapp_agent(
    agent_id: int,
    payload: WhatsappAgentUpdatePayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = db.query(TextAgent).filter(
        TextAgent.id == agent_id,
        TextAgent.user_id == current_user.id,
        TextAgent.channel == "whatsapp"
    ).first()

    if not agent:
        raise HTTPException(404, "WhatsApp agent not found")

    if payload.name is not None:
        agent.name = payload.name
    if payload.instructions is not None:
        agent.instructions = payload.instructions
    if payload.startup_message is not None:
        agent.startup_message = payload.startup_message
    if payload.onboarding_mode is not None:
        agent.onboarding_mode = payload.onboarding_mode
    if payload.enable_mcp_server is not None:
        agent.enable_mcp_server = payload.enable_mcp_server

    config = agent.whatsapp_config
    if config:
        if payload.phone_number is not None:
            config.phone_number = payload.phone_number
        if payload.phone_number_id is not None:
            config.phone_number_id = payload.phone_number_id

    db.commit()
    db.refresh(agent)

    return {"status": "success", "message": "WhatsApp agent updated"}


# ──────────────────────────────────────────────────────────────
# 1d. Delete WhatsApp Agent
# ──────────────────────────────────────────────────────────────
@router.delete("/agents/{agent_id}")
async def delete_whatsapp_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = db.query(TextAgent).filter(
        TextAgent.id == agent_id,
        TextAgent.user_id == current_user.id,
        TextAgent.channel == "whatsapp"
    ).first()

    if not agent:
        raise HTTPException(404, "WhatsApp agent not found")

    # Clean up linked config
    if agent.whatsapp_config:
        db.delete(agent.whatsapp_config)
    
    db.delete(agent)
    db.commit()

    return {"status": "success", "message": "WhatsApp agent deleted"}


@router.post("/agents/{agent_id}/send-login-url")
async def send_login_url(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = db.query(TextAgent).filter(
        TextAgent.id == agent_id,
        TextAgent.user_id == current_user.id
    ).first()

    if not agent:
        raise HTTPException(404, "WhatsApp agent not found")

    config = agent.whatsapp_config
    
    if not config or not config.dashboard_slug:
        # Fallback in case slug is missing
        from app.utils.slug import generate_dashboard_slug
        if not config:
            config = WhatsappConfig(text_agent_id=agent.id, status="pending")
            db.add(config)
            db.flush()
        config.dashboard_slug = generate_dashboard_slug(agent.name, agent.id)
        db.commit()

    login_url = f"{settings.frontend_base_url}/agent-login/{config.dashboard_slug}"
    
    # Send to owner + all active employees
    to_emails = [current_user.email]
    employees = db.query(HumanAgent).filter(
        HumanAgent.user_id == current_user.id,
        HumanAgent.is_active == True
    ).all()
    
    if employees:
        to_emails.extend([e.email for e in employees])

    subject = f"Login URL for Your Dashboard: {current_user.username}"
    
    success_count = 0
    from app.tasks.email_task import send_email_task
    
    for email in to_emails:
        email_html = f"""
        <html>
            <body style='font-family: Arial, sans-serif;'>
                <h3>WhatsApp Agent Dashboard Access</h3>
                <p>Hello,</p>
                <p>You can log in to manage conversations at:</p>
                <div style='background: #f1f5f9; padding: 15px; border-radius: 8px;'>
                    <p><a href="{login_url}">{login_url}</a></p>
                </div>
                <hr/>
                <p>Thank you for using our platform.</p>
            </body>
        </html>
        """
        try:
            send_email_task.delay(email, subject, email_html)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")

    return {"status": "success", "message": f"Login URL sent to {success_count} recipients"}


# ──────────────────────────────────────────────────────────────
# 2. Connect WhatsApp (updates whatsapp_configs)
# ──────────────────────────────────────────────────────────────
@router.get("/connect/{text_agent_id}")
async def start_whatsapp_connect(
    text_agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = db.query(TextAgent).filter(
        TextAgent.id == text_agent_id,
        TextAgent.user_id == current_user.id,
        TextAgent.channel == "whatsapp"
    ).first()

    if not agent:
        raise HTTPException(404, "Agent not found")

    # Build Meta OAuth URL
    redirect_uri = settings.WHATSAPP_REDIRECT_URI or f"{settings.api_base_url}/api/whatsapp/oauth/callback"
    state = str(text_agent_id)  # pass agent ID in state

    oauth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth"
        f"?client_id={settings.WHATSAPP_APP_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
        f"&scope=whatsapp_business_management,whatsapp_business_messaging,business_management"
        f"&response_type=code"
    )

    return {"redirect_url":oauth_url}

# ──────────────────────────────────────────────────────────────
# 3. Status Check
# ──────────────────────────────────────────────────────────────
@router.get("/status/{text_agent_id}", response_model=WhatsappConnectionStatus)
async def get_whatsapp_status(
    text_agent_id: int,
    request: Request,  # ← correct, no Depends
    db: Session = Depends(get_db)
):
    text_agent = db.query(TextAgent).filter(
        TextAgent.id == text_agent_id,
        TextAgent.channel == "whatsapp"
    ).first()

    if not text_agent:
        raise HTTPException(404, "WhatsApp text agent not found")

    config = text_agent.whatsapp_config

    return WhatsappConnectionStatus(
        text_agent_id=text_agent_id,
        connected=bool(config and config.status in ("connected", "connected_demo")),
        status=config.status if config else "not_connected",
        phone_number_id=config.phone_number_id if config else None,
        phone_number=config.phone_number if config else None,
        updated_at=config.updated_at if config else None
    )


@router.get("/oauth/callback")
async def whatsapp_oauth_callback(request: Request, db: Session = Depends(get_db)):
    """
    Meta OAuth callback - handles token in fragment (#access_token=...) and query string.
    """
    url_str = str(request.url)
    logger.info(f"OAuth callback hit with URL: {url_str}")
    redirect_uri = settings.WHATSAPP_REDIRECT_URI or f"{settings.api_base_url}/api/whatsapp/oauth/callback"

    # Step 1: If token/state is in fragment (#...), redirect to same path with query string
    if '#' in url_str:
        fragment = url_str.split('#')[1]
        new_url = url_str.split('#')[0] + '?' + fragment
        logger.info(f"Fragment detected - redirecting to: {new_url}")

        return HTMLResponse(f"""
        <html>
            <head>
                <title>Connecting WhatsApp...</title>
                <script>
                    window.location.replace("{new_url}");
                </script>
            </head>
            <body style="font-family:sans-serif; text-align:center; padding:100px;">
                <p>Connecting... Please wait (1-2 seconds)...</p>
            </body>
        </html>
        """)

    # Step 2: Now params are in query string
    params = request.query_params
    logger.debug(f"Query params after redirect: {params}")

    state = params.get("state")
    access_token = params.get("access_token")
    code = params.get("code")
    error = params.get("error")
    error_reason = params.get("error_reason")
    error_description = params.get("error_description")

    # Handle Meta errors (user cancelled, denied, etc.)
    if error:
        logger.warning(f"Meta OAuth error: {error} - {error_description or error_reason}")
        frontend_url = settings.FRONTEND_URL or "http://localhost:3000/dashboard"
        return HTMLResponse(f"""
        <html>
            <body style="font-family:sans-serif; text-align:center; padding:100px; color:#d32f2f;">
                <h1>Connection Failed</h1>
                <p>{error_description or error_reason or error}</p>
                <p>Please try connecting again from your dashboard.</p>
                <p><a href="{frontend_url}">Back to Dashboard</a></p>
            </body>
        </html>
        """, status_code=400)

    # Missing state → invalid flow
    if not state:
        logger.error("Missing state in callback after fragment handling")
        return HTMLResponse("""
        <html>
            <body style="font-family:sans-serif; text-align:center; padding:100px; color:#d32f2f;">
                <h1>Error</h1>
                <p>Missing state parameter. Please try connecting again from dashboard.</p>
                <p><a href="{settings.FRONTEND_URL or 'http://localhost:3000/dashboard'}">Back</a></p>
            </body>
        </html>
        """, status_code=400)

    # Parse state (text_agent_id)
    try:
        text_agent_id = int(state)
    except ValueError:
        logger.error(f"Invalid state value: {state}")
        raise HTTPException(400, "Invalid state parameter")

    # Find config
    config = db.query(WhatsappConfig).filter(
        WhatsappConfig.text_agent_id == text_agent_id
    ).first()

    if not config:
        logger.error(f"Config not found for text_agent_id: {text_agent_id}")
        raise HTTPException(404, "WhatsApp config not found")

    final_token = access_token

    # If we got authorization code (code flow), exchange it for token
    if code and not final_token:
        logger.info(f"Exchanging code for token: {code[:10]}...")
        try:
            async with httpx.AsyncClient() as client:
                token_resp = await client.get(
                    "https://graph.facebook.com/v18.0/oauth/access_token",
                    params={
                        "client_id": settings.WHATSAPP_APP_ID,
                        "client_secret": settings.WHATSAPP_APP_SECRET,
                        "redirect_uri": redirect_uri,
                        "code": code
                    }
                )
                token_data = token_resp.json()
                logger.debug(f"Token exchange response: {token_data}")

                if "access_token" in token_data:
                    final_token = token_data["access_token"]
                else:
                    logger.error(f"Token exchange failed: {token_data}")
                    raise HTTPException(400, "Failed to exchange authorization code")

        except Exception as e:
            logger.exception("Token exchange error")
            raise HTTPException(500, f"Token exchange error: {str(e)}")

    if not final_token:
        logger.error("No access token received from Meta")
        raise HTTPException(400, "No access token received")

    # Validate token with debug_token
    try:
        async with httpx.AsyncClient() as client:
            debug_resp = await client.get(
                "https://graph.facebook.com/v18.0/debug_token",
                params={
                    "input_token": final_token,
                    "access_token": f"{settings.WHATSAPP_APP_ID}|{settings.WHATSAPP_APP_SECRET}"
                }
            )
            debug_data = debug_resp.json().get("data", {})
            logger.debug(f"Debug token response: {debug_data}")

            if not debug_data.get("is_valid"):
                logger.warning(f"Invalid token received: {debug_data}")
                raise HTTPException(400, "Received invalid or expired token")

            business_id = debug_data.get("business_id") or debug_data.get("issued_to") or "unknown"

    except Exception as e:
        logger.exception("Debug token error")
        business_id = "unknown"

    # Save to config
    config.access_token = final_token
    config.business_id = business_id
    config.status = "connected"
    config.connected_at = datetime.utcnow()

    db.commit()

    logger.info(f"WhatsApp connected successfully for agent {text_agent_id}")

    # Success page with auto-redirect and popup close
    frontend_url = f"{settings.frontend_base_url}/"

    return HTMLResponse(f"""
    <html>
        <head>
            <title>WhatsApp Connected</title>
            <meta http-equiv="refresh" content="3;url={frontend_url}">
        </head>
        <body style="font-family:sans-serif; text-align:center; padding:100px;">
            <h1 style="color:#25D366;">WhatsApp Connected Successfully!</h1>
            <p>Redirecting back to dashboard in 3 seconds...</p>
            <p>If not redirected, <a href="{frontend_url}">click here</a>.</p>
            <script>
                setTimeout(() => {{
                    window.close();  // Close popup if opened in one
                }}, 3000);
            </script>
        </body>
    </html>
    """)
@router.get("/{text_agent_id}/widget-code", response_class=PlainTextResponse)
async def get_widget_code(
    text_agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    text_agent = db.query(TextAgent).filter(
        TextAgent.id == text_agent_id,
        TextAgent.user_id == current_user.id,
        TextAgent.channel == "whatsapp"
    ).first()

    if not text_agent:
        raise HTTPException(404, "Text agent not found")

    widget_url = f"{settings.api_base_url}/api/whatsapp/widget.js"
    api_base = settings.api_base_url

    embed_code = f"""<!-- WhatsApp Agent Widget - {text_agent.name} -->
<script src="{widget_url}" 
        data-text-agent-id="{text_agent_id}"
        data-api-base="{api_base}">
</script>"""

    return embed_code

@router.get("/widget.js", response_class=FileResponse)
async def serve_widget_js():
    """
    Serves the WhatsApp widget JavaScript file publicly.
    - No auth required (end-users need this on their sites)
    - Cached by browser for 1 hour
    """
    if not WIDGET_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Widget JS file not found on server. Check path: " + str(WIDGET_FILE)
        )

    return FileResponse(
        path=WIDGET_FILE,
        media_type="application/javascript",
        filename="widget.js",
        headers={
            "Cache-Control": "public, max-age=3600",  # cache 1 hour
            "Access-Control-Allow-Origin": "*",        # allow cross-site embedding
        }
    )
@router.get("/chat", response_class=HTMLResponse)
async def serve_chat_page():
    """Serves the fallback chat HTML page"""
    chat_file = Path(__file__).parent.parent / "static" / "chat.html"
    if not chat_file.exists():
        raise HTTPException(404, "Chat page not found")
    return HTMLResponse(content=chat_file.read_text())

@router.post("/chat/ai")
async def chat_ai_fallback(
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Handles fallback web chat using the same AI logic as WhatsApp.
    payload: { text_agent_id, message, customer }
    """
    text_agent_id = payload.get("text_agent_id")
    message = payload.get("message")
    customer = payload.get("customer", "WebUser")

    text_agent = db.query(TextAgent).filter(TextAgent.id == text_agent_id).first()
    if not text_agent:
        raise HTTPException(404, "Agent not found")

    # 1. FIND OR CREATE CONTACT
    contact = db.query(Contact).filter(
        Contact.identifier == customer
    ).first()
    if not contact:
        contact = Contact(identifier=customer)
        db.add(contact)
        db.commit()
        db.refresh(contact)

    # 2. FIND OR CREATE CONVERSATION
    conversation = db.query(Conversation).filter(
        Conversation.contact_id == contact.id,
        Conversation.text_agent_id == text_agent.id
    ).first()
    if not conversation:
        conversation = Conversation(
            contact_id=contact.id,
            text_agent_id=text_agent.id
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 3. SAVE INCOMING MESSAGE
    db_msg = Message(
        conversation_id=conversation.id,
        content=message,
        is_from_contact=True
    )
    db.add(db_msg)
    conversation.last_message_at = datetime.utcnow()
    db.commit()

    # Log to file
    log_message(conversation.id, "User (Web)", message)

    user_message = message.strip().lower()

    # 4. CHECK HANDOFF TRIGGER
    handoff_trigger_phrases = ["human", "i want to talk to human", "agent", "support"]
    if any(phrase in user_message for phrase in handoff_trigger_phrases):
        conversation.is_human_active = True
        conversation.human_agent_id = None
        
        confirmation_msg = "Connecting you to an agent, please wait... 🤝"
        confirm_db_msg = Message(
            conversation_id=conversation.id,
            content=confirmation_msg,
            is_from_contact=False,
            is_from_agent=True
        )
        db.add(confirm_db_msg)
        db.commit() # Atomic commit for flag and message
        
        log_message(conversation.id, "System", confirmation_msg)

        # Broadcast to dashboard
        await manager.broadcast({
            "type": "new_handover",
            "id": conversation.id,
            "customer": customer,
            "identifier": customer,
            "timestamp": datetime.utcnow().isoformat(),
            "owner_id": text_agent.user_id
        }, agent_id=str(text_agent.user_id))

        return {"response": confirmation_msg, "is_human_active": True}

    # 5. REUSE AI LOGIC
    if conversation.is_human_active:
        # If already in human mode, broadcast message to dashboard
        await manager.broadcast({
            "type": "new_message",
            "whatsapp_number": customer,
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        }, agent_id=str(text_agent.user_id))

        # Sync to HubSpot if enabled
        if text_agent.enable_mcp_server:
            sync_to_hubspot_task.delay(conversation.id)

        return {"response": "An agent will respond shortly.", "is_human_active": True}

    from app.routes.text_ai import AIChatRequest, generate_ai_chat
    ai_request = AIChatRequest(
        text_agent_id=text_agent_id,
        message=message
    )
    
    ai_resp = await generate_ai_chat(ai_request, None, db)
    reply = ai_resp.reply if ai_resp.success else "Sorry, I'm having trouble thinking."

    # Save and Log AI message
    ai_msg = Message(
        conversation_id=conversation.id,
        content=reply,
        is_from_contact=False,
        is_from_agent=False
    )
    db.add(ai_msg)
    db.commit()
    log_message(conversation.id, "AI", reply)

    # Sync to HubSpot if enabled
    if text_agent.enable_mcp_server:
        sync_to_hubspot_task.delay(conversation.id)

    return {"response": reply}

VERIFY_TOKEN = "ldt_verify_123"

@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)

    raise HTTPException(status_code=403, detail="Webhook verification failed")


# =====================================================
# RECEIVE WHATSAPP MESSAGES
# =====================================================
@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        logger.info(f"Webhook received: {json.dumps(data, indent=2)}")

        if data.get("object") != "whatsapp_business_account":
            return {"status": "ignored"}

        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                if "messages" not in value:
                    continue

                message = value["messages"][0]
                sender = message.get("from")
                text = message.get("text", {}).get("body", "")

                if not text:
                    continue

                metadata = value.get("metadata", {})
                phone_number_id = metadata.get("phone_number_id")

                # -------------------------------------------------
                # FIND WHATSAPP CONFIG
                # -------------------------------------------------
                config = db.query(WhatsappConfig).filter(
                    WhatsappConfig.phone_number_id == phone_number_id
                ).first()

                if not config:
                    logger.warning(f"No config found for {phone_number_id}")
                    continue

                text_agent = config.text_agent
                if not text_agent:
                    logger.warning("No text agent linked")
                    continue

                # Get profile name from contacts list in webhook
                profile_name = None
                if "contacts" in value:
                    profile_name = value["contacts"][0].get("profile", {}).get("name")

                # -------------------------------------------------
                # FIND OR CREATE CONTACT
                # -------------------------------------------------
                contact = db.query(Contact).filter(
                    Contact.identifier == sender
                ).first()

                if not contact:
                    contact = Contact(identifier=sender, name=profile_name)
                    db.add(contact)
                    db.commit()
                    db.refresh(contact)
                elif profile_name and not contact.name:
                    contact.name = profile_name
                    db.commit()

                # -------------------------------------------------
                # FIND OR CREATE CONVERSATION
                # -------------------------------------------------
                conversation = db.query(Conversation).filter(
                    Conversation.contact_id == contact.id,
                    Conversation.text_agent_id == text_agent.id
                ).first()

                if not conversation:
                    conversation = Conversation(
                        contact_id=contact.id,
                        text_agent_id=text_agent.id
                    )
                    db.add(conversation)
                    db.commit()
                    db.refresh(conversation)

                # -------------------------------------------------
                # SAVE INCOMING MESSAGE
                # -------------------------------------------------
                incoming_msg = Message(
                    conversation_id=conversation.id,
                    content=text,
                    is_from_contact=True
                )
                db.add(incoming_msg)

                db.commit()
                
                # Log incoming message
                log_message(conversation.id, "User", text)

                # Sync to HubSpot if enabled
                if text_agent.enable_mcp_server:
                    sync_to_hubspot_task.delay(conversation.id)

                user_message = text.strip().lower()

                # =================================================
                # 🔥 HUMAN TRIGGER LOGIC
                # =================================================
                handoff_trigger_phrases = ["human", "i want to talk to human", "agent", "support"]
                if any(phrase in user_message for phrase in handoff_trigger_phrases):

                    # Always set is_human_active to True so it enters the shared company queue
                    conversation.is_human_active = True
                    conversation.human_agent_id = None # Leaves it unassigned so any agent can claim it
                    db.commit()

                    confirmation_msg = (
                        "Connecting you to an agent, please wait... 🤝"
                    )

                    # Save confirmation message
                    confirm_message = Message(
                        conversation_id=conversation.id,
                        content=confirmation_msg,
                        is_from_contact=False,
                        is_from_agent=True
                    )
                    db.add(confirm_message)
                    db.commit()
                    
                    # Log handoff confirmation
                    log_message(conversation.id, "System", confirmation_msg)

                    # Send confirmation to WhatsApp
                    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

                    headers = {
                        "Authorization": f"Bearer {config.access_token}",
                        "Content-Type": "application/json"
                    }

                    payload = {
                        "messaging_product": "whatsapp",
                        "to": sender,
                        "type": "text",
                        "text": {"body": confirmation_msg}
                    }

                    async with httpx.AsyncClient() as client:
                        await client.post(url, headers=headers, json=payload)

                    # 3. Broadcast to dashboard for real-time refresh
                    await manager.broadcast({
                        "type": "new_handover",
                        "id": conversation.id,
                        "customer": sender,
                        "identifier": sender,
                        "timestamp": datetime.utcnow().isoformat(),
                        "owner_id": text_agent.user_id
                    }, agent_id=str(text_agent.user_id))

                    return {"status": "handoff_triggered"}

                # =================================================
                # 🔥 HUMAN ACTIVE CHECK
                # =================================================
                if conversation.is_human_active:
                    logger.info(f"Human takeover active for {sender}. Broadcasting to dashboard.")
                    
                    # 1. Broadcast to dashboard
                    await manager.broadcast({
                        "type": "new_message",
                        "whatsapp_number": sender,
                        "content": text,
                        "conversation_id": conversation.id,
                        "timestamp": datetime.utcnow().isoformat()
                    }, agent_id=str(text_agent.user_id))
                    
                    # Sync to HubSpot if enabled (ensure info is captured even if agent hasn't replied)
                    if text_agent.enable_mcp_server:
                        sync_to_hubspot_task.delay(conversation.id)

                    return {"status": "human_active"}

                # =================================================
                # 🤖 CALL AI
                # =================================================
                ai_req = AIChatRequest(
                    text_agent_id=text_agent.id,
                    message=text
                )

                ai_resp = await generate_ai_chat(
                    req=ai_req,
                    current_user=None,
                    db=db
                )

                reply = (
                    ai_resp.reply
                    if ai_resp.success
                    else "Sorry, something went wrong."
                )

                # =================================================
                # 🔥 AI-INITIATED HANDOFF CHECK
                # =================================================
                if "i am connecting to you the human agent" in reply.lower():
                    logger.info(f"AI initiated handoff for {sender}")
                    conversation.is_human_active = True
                    db.commit()
                    
                    # Broadcast to dashboard
                    await manager.broadcast({
                        "type": "new_handover",
                        "id": conversation.id,
                        "customer": sender,
                        "identifier": sender,
                        "timestamp": datetime.utcnow().isoformat(),
                        "owner_id": text_agent.user_id
                    }, agent_id=str(text_agent.user_id))

                # Save AI message
                ai_msg = Message(
                    conversation_id=conversation.id,
                    content=reply,
                    is_from_contact=False,
                    is_from_agent=False
                )
                db.add(ai_msg)
                db.commit()
                
                # Log AI response
                log_message(conversation.id, "AI", reply)

                # Sync to HubSpot if enabled
                if text_agent.enable_mcp_server:
                    sync_to_hubspot_task.delay(conversation.id)

                # Send AI reply
                url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

                headers = {
                    "Authorization": f"Bearer {config.access_token}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "messaging_product": "whatsapp",
                    "to": sender,
                    "type": "text",
                    "text": {"body": reply}
                }

                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        url,
                        headers=headers,
                        json=payload
                    )

                    logger.info(f"Reply sent - status: {resp.status_code}")
                    logger.info(f"Response: {resp.text}")

        return {"status": "success"}

    except Exception:
        logger.exception("Webhook processing error")
        return {"status": "error"}
    
@router.get("/dashboard/{slug}")
def dashboard(slug: str, db: Session = Depends(get_db)):
    config = db.query(WhatsappConfig).filter(
        WhatsappConfig.dashboard_slug == slug
    ).first()
    if not config:
        raise HTTPException(404, "Dashboard not found")
    
    # return details for frontend
    return {
        "agent_name": config.text_agent.name,
        "phone_number": config.phone_number,
        "assigned_users": [],
    }
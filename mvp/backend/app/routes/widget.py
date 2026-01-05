"""
Widget code generation routes and WebSocket handler
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Header
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models.user import User
from app.models.assistant_config import AssistantConfig
from app.models.openai_key import OpenAIKey
from app.models.service_account_key import ServiceAccountKey
from app.models.agent import Agent
from app.models.interaction import Interaction
from app.schemas import WidgetCodeResponse
from app.dependencies import get_current_user
from app.utils.encryption import decrypt_api_key
from app.utils.openai_logger import log_openai_websocket_connect, log_openai_websocket_message
from app.config import settings
from pathlib import Path
import uuid
import json
import asyncio
import websockets
from datetime import datetime
from typing import Optional, Dict
from urllib.parse import urlparse

router = APIRouter(prefix="/api/widget", tags=["widget"])

# Widget static files directory
WIDGET_DIR = Path(__file__).parent.parent.parent / "widget"


def format_instructions_for_openai(instructions: str) -> str:
    """
    Convert instructions from JSON format to plain text format for OpenAI.
    Enhanced with ultra-strict response length constraints for cost optimization.
    
    Args:
        instructions: Instructions as JSON string or plain text
        
    Returns:
        Plain text instructions formatted for OpenAI with strict response length limits
    """
    if not instructions:
        return ""
    
    # ULTRA-STRICT RESPONSE LENGTH RULES - ENFORCE AT ALL TIMES
    response_length_rules = """⚠️ CRITICAL RESPONSE LENGTH RULES - MANDATORY ENFORCEMENT ⚠️

1. MAXIMUM LENGTH: Your response MUST be EXACTLY 2-3 lines maximum. NEVER exceed 3 lines.
2. WORD COUNT: Your response MUST be between 40-45 words maximum. Count your words before responding.
3. SHORTER IS BETTER: If you can answer in 1-2 lines (20-30 words), DO IT. Only use 2-3 lines if absolutely necessary.
4. NO EXCEPTIONS: These limits apply to ALL responses, regardless of question complexity.
5. BULLET POINTS: For lists or multiple items, use bullet points (•) to stay within limits.
6. DIRECT ANSWERS: Get straight to the point. No greetings, no fluff, no unnecessary words.
7. PRIORITIZE: If multiple points exist, mention only the most important 1-2 points.

Example of CORRECT response (2 lines, ~42 words):
"Complex decisions involve judgment and context. Examples: resource allocation, risk management, and customer support. These require data analysis and human judgment for dynamic scenarios."

Example of WRONG response (too long):
[Any response over 3 lines or 45 words is WRONG and must be shortened]

REMEMBER: Every word counts. Be concise. Be direct. Stay within limits."""
    
    # Try to parse as JSON
    try:
        instructions_dict = json.loads(instructions)
        
        # If it's a dict, format it as readable text
        if isinstance(instructions_dict, dict):
            formatted_parts = [response_length_rules]
            
            # Add each field as a section
            if instructions_dict.get("voice_behaviour"):
                formatted_parts.append(f"\nVOICE & BEHAVIOUR\n{instructions_dict['voice_behaviour']}")
            
            if instructions_dict.get("scope"):
                formatted_parts.append(f"\nSCOPE\n{instructions_dict['scope']}")
            
            if instructions_dict.get("contact_details"):
                formatted_parts.append(f"\nCONTACT DETAILS\n{instructions_dict['contact_details']}")
            
            if instructions_dict.get("privacy_rules"):
                formatted_parts.append(f"\nPRIVACY RULES\n{instructions_dict['privacy_rules']}")
            
            if instructions_dict.get("top_features"):
                formatted_parts.append(f"\nTOP FEATURES\n{instructions_dict['top_features']}")
            
            if instructions_dict.get("product"):
                formatted_parts.append(f"\nPRODUCT\n{instructions_dict['product']}")
            
            if instructions_dict.get("services"):
                formatted_parts.append(f"\nSERVICES\n{instructions_dict['services']}")
            
            if instructions_dict.get("office_locations"):
                formatted_parts.append(f"\nOFFICE LOCATIONS\n{instructions_dict['office_locations']}")
            
            if instructions_dict.get("pricing_rules"):
                formatted_parts.append(f"\nPRICING RULES\n{instructions_dict['pricing_rules']}")
            
            if instructions_dict.get("restrictions"):
                formatted_parts.append(f"\nRESTRICTIONS\n{instructions_dict['restrictions']}")
            
            if instructions_dict.get("tone_examples"):
                formatted_parts.append(f"\nTONE EXAMPLES\n{instructions_dict['tone_examples']}")
            
            if instructions_dict.get("additional_instructions"):
                formatted_parts.append(f"\nADDITIONAL INSTRUCTIONS\n{instructions_dict['additional_instructions']}")
            
            return "\n".join(formatted_parts)
        else:
            # If parsed but not a dict, return as string with rules
            return f"{response_length_rules}\n\n{str(instructions_dict)}"
    except (json.JSONDecodeError, TypeError):
        # If it's not JSON, return as plain text with rules
        return f"{response_length_rules}\n\n{instructions}"


@router.get("/widget.css")
async def get_widget_css():
    """Serve widget CSS file"""
    css_file = WIDGET_DIR / "widget.css"
    if not css_file.exists():
        raise HTTPException(status_code=404, detail="Widget CSS not found")
    return FileResponse(css_file, media_type="text/css")
@router.get("/widget-static.css")
async def get_widget_css():
    """Serve widget CSS file"""
    css_file = WIDGET_DIR / "widget-static.css"
    if not css_file.exists():
        raise HTTPException(status_code=404, detail="Widget CSS not found")
    return FileResponse(css_file, media_type="text/css")


@router.get("/widget.js")
async def get_widget_js():
    """Serve widget JavaScript file"""
    js_file = WIDGET_DIR / "widget.js"
    if not js_file.exists():
        raise HTTPException(status_code=404, detail="Widget JS not found")
    return FileResponse(js_file, media_type="application/javascript")
@router.get("/widget-static.js")
async def get_widget_static_js():
    js_file = WIDGET_DIR / "widget-static.js"
    if not js_file.exists():
        raise HTTPException(status_code=404, detail="Widget Static JS not found")
    return FileResponse(js_file, media_type="application/javascript")

@router.get("/codeFixed/agent/{agent_id}", response_model=WidgetCodeResponse)
async def generate_agent_widget_code(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate JavaScript code for a specific agent widget"""
    # Get the agent
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Try to parse instructions as JSON (for debugging/optional use)
    try:
        if agent.instructions:
            instructions_data = json.loads(agent.instructions)
            company_name = instructions_data.get("company_name")
            if company_name:
                print(f"Company name: {company_name}")
    except (json.JSONDecodeError, TypeError):
        # Instructions might be plain text, which is fine
        pass
    
    # Get the OpenAI key for this agent
    api_key = db.query(ServiceAccountKey).filter(
        ServiceAccountKey.id == agent.openai_key_id,
        ServiceAccountKey.is_active == True
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent's API key is not active"
        )
    
    # Generate unique widget ID
    widget_id = str(uuid.uuid4())
  
   
    
    # Use API base URL from settings (can be configured via environment variables)
    api_base_url = settings.api_base_url
    
    # Generate minimal widget code that loads external files

    widget_code = f"""<!-- Voice Assistant Widget: {agent.name} -->
<script>
(function() {{
    // API base URL for widget backend connection
    let apiBaseUrl = '{api_base_url}';
    
    // Create and load widget script
    const script = document.createElement('script');
    script.src = apiBaseUrl.replace(/\/$/, '') + '/api/widget/widget-static.js';
    script.setAttribute('data-agent-id', '{agent_id}');
    script.setAttribute('data-api-url', apiBaseUrl);
    script.setAttribute('data-agent-name', '{agent.name}');
    script.setAttribute('data-target-id', 'chatbot'); // <<<--- Change to desired container id
    script.async = true;
    document.head.appendChild(script);
}})();
</script>"""
    
    return {
        "widget_code": widget_code.strip(),
        "widget_id": widget_id,
        "assistant_id": agent_id,
        "assistant_name": agent.name
    }
@router.get("/code/agent/{agent_id}", response_model=WidgetCodeResponse)
async def generate_agent_widget_code(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate JavaScript code for a specific agent widget"""
    # Get the agent
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.id
    ).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Try to parse instructions as JSON (for debugging/optional use)
    try:
        if agent.instructions:
            instructions_data = json.loads(agent.instructions)
            company_name = instructions_data.get("company_name")
            if company_name:
                print(f"Company name: {company_name}")
    except (json.JSONDecodeError, TypeError):
        # Instructions might be plain text, which is fine
        pass
    
    # Get the OpenAI key for this agent
    api_key = db.query(ServiceAccountKey).filter(
        ServiceAccountKey.id == agent.openai_key_id,
        ServiceAccountKey.is_active == True
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent's API key is not active"
        )
    
    # Generate unique widget ID
    widget_id = str(uuid.uuid4())
  
   
    
    # Use API base URL from settings (can be configured via environment variables)
    api_base_url = settings.api_base_url
    
    # Generate minimal widget code that loads external files

    widget_code = f"""<!-- Voice Assistant Widget: {agent.name} -->
<script>
(function() {{
    // API base URL for widget backend connection
    let apiBaseUrl = '{api_base_url}';
    
    // Create and load widget script-
    const script = document.createElement('script');
    script.src = apiBaseUrl.replace(/\/$/, '') + '/api/widget/widget.js';
    script.setAttribute('data-agent-id', '{agent_id}');
    script.setAttribute('data-api-url', apiBaseUrl);
    script.setAttribute('data-agent-name', '{agent.name}');
    script.async = true;
    
    document.head.appendChild(script);
}})();
</script>"""
    
    return {
        "widget_code": widget_code.strip(),
        "widget_id": widget_id,
        "assistant_id": agent_id,
        "assistant_name": agent.name
    }
@router.get("/code/{assistant_id}", response_model=WidgetCodeResponse)
async def generate_widget_code(
    assistant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate JavaScript code for a specific assistant chatbot widget"""
    # Get the assistant config
    config = db.query(AssistantConfig).filter(
        AssistantConfig.id == assistant_id,
        AssistantConfig.user_id == current_user.id
    ).first()
  
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found"
        )
    
    # Get active OpenAI key
    active_key = db.query(ServiceAccountKey).filter(
        ServiceAccountKey.user_id == current_user.id,
        ServiceAccountKey.is_active == True
    ).first()
    
    if not active_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active OpenAI API key found. Please add an API key first."
        )
    
    # Get agent configuration if configured
    agent = None
    if config.agent_id:
        agent = db.query(Agent).filter(Agent.id == config.agent_id).first()
    
    # Generate unique widget ID
    widget_id = str(uuid.uuid4())
    
    # Generate widget code
    widget_code = f"""
<!-- Voice Assistant Widget: {config.name} -->
<script>
(function() {{
    const widgetId = '{widget_id}';
    const assistantId = {assistant_id};
    const apiBaseUrl = window.location.protocol + '//' + window.location.host;
    
    // Widget initialization code
    // This will connect to your backend WebSocket proxy
    // Implementation details will be added based on your backend WebSocket setup
    
    console.log('Voice Assistant Widget Loaded:', widgetId, 'for Assistant:', assistantId);
    
    // TODO: Implement widget initialization
    // - Create widget UI
    // - Connect to backend WebSocket proxy
    // - Handle audio input/output
    // - Display transcriptions
}})();
</script>
"""
    
    return {
        "widget_code": widget_code.strip(),
        "widget_id": widget_id,
        "assistant_id": assistant_id,
        "assistant_name": config.name
    }


# WebSocket connection tracking
client_connections: Dict[WebSocket, websockets.WebSocketClientProtocol] = {}
# Track interactions for each WebSocket connection
websocket_interactions: Dict[WebSocket, int] = {}  # Maps WebSocket to Interaction ID

# Track token usage per WebSocket session (accumulated from response.done events)
websocket_usage: Dict[WebSocket, dict] = {}  # Maps WebSocket to usage data


def validate_domain(request_domain: str, agent_domain: str) -> bool:
    """Validate that request domain matches agent's allowed domain"""
    if not request_domain or not agent_domain:
        return False
    
    # Normalize domains (remove protocol, www, trailing slashes)
    request_domain = request_domain.lower().strip()
    agent_domain = agent_domain.lower().strip()
    
    # Remove protocol if present
    if "://" in request_domain:
        request_domain = urlparse(request_domain).netloc
    if "://" in agent_domain:
        agent_domain = urlparse(agent_domain).netloc
    
    # Remove port numbers for comparison (localhost:3000 -> localhost)
    if ":" in request_domain:
        request_domain = request_domain.split(":")[0]
    if ":" in agent_domain:
        agent_domain = agent_domain.split(":")[0]
    
    # Remove www prefix for comparison
    request_domain = request_domain.replace("www.", "")
    agent_domain = agent_domain.replace("www.", "")
    
    # Special handling for localhost and 127.0.0.1
    # They should be considered equivalent
    localhost_variants = ["localhost", "127.0.0.1"]
    if (request_domain in localhost_variants) and (agent_domain in localhost_variants):
        return True
    
    # Check exact match or subdomain match
    return request_domain == agent_domain or request_domain.endswith("." + agent_domain)


@router.websocket("/ws")
async def widget_websocket(
    websocket: WebSocket,
    agent_id: int,
    origin: Optional[str] = Header(None)
):
    """
    WebSocket endpoint for widget connections
    Validates domain, fetches agent, and proxies to OpenAI Realtime API
    """
    await websocket.accept()
    print(f"[Widget WS] Client connected, agent_id={agent_id}, origin={origin}")
    
    # Create database session manually for WebSocket
    db = SessionLocal()
    openai_ws = None
    agent = None
    
    try:
        # Fetch agent from database
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        
        if not agent:
            await websocket.send_json({
                "type": "error",
                "error": f"Agent {agent_id} not found"
            })
            await websocket.close()
            return
        
        # Validate domain
        if origin:
            request_domain = urlparse(origin).netloc if "://" in origin else origin
            if not validate_domain(request_domain, agent.domain):
                await websocket.send_json({
                    "type": "error",
                    "error": f"Domain validation failed. Expected: {agent.domain}, Got: {request_domain}"
                })
                await websocket.close()
                print(f"[Widget WS] Domain validation failed: {request_domain} != {agent.domain}")
                return
        
        # Get OpenAI API key
        api_key_record = db.query(OpenAIKey).filter(
            ServiceAccountKey.id == agent.openai_key_id,
            ServiceAccountKey.is_active == True
        ).first()
        
        if not api_key_record:
            await websocket.send_json({
                "type": "error",
                "error": "Agent's API key is not active"
            })
            await websocket.close()
            return
        
        # Decrypt API key
        try:
            openai_api_key = decrypt_api_key(api_key_record.encrypted_key)
        except Exception as e:
            print(f"[Widget WS] Error decrypting API key: {e}")
            await websocket.send_json({
                "type": "error",
                "error": "Failed to decrypt API key"
            })
            await websocket.close()
            return
        
        print(f"[Widget WS] Agent '{agent.name}' validated, connecting to OpenAI...")
        
        # Connect to OpenAI Realtime API (requested cheaper mini preview)
        ws_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview"
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        # Log WebSocket connection in dev environment
        log_openai_websocket_connect(ws_url, headers)
        
        try:
            openai_ws = await websockets.connect(ws_url, extra_headers=headers)
            print("[Widget WS] Connected to OpenAI Realtime API")
        except Exception as e:
            print(f"[Widget WS] OpenAI connection failed: {e}")
            await websocket.send_json({
                "type": "error",
                "error": "Failed to connect to OpenAI"
            })
            await websocket.close()
            return
        
        # Configure OpenAI session with agent settings
        agent_config = agent.agent_config if agent.agent_config else {}
        
        session_payload = {
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1"},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": float(agent.noise_reduction_threshold) if agent.noise_reduction_threshold else 0.6,  # Higher = less sensitive, fewer false starts
                    "prefix_padding_ms": agent.noise_reduction_prefix_padding_ms or 200,  # Reduced from 300
                    "silence_duration_ms": agent.noise_reduction_silence_duration_ms or 700  # Increased from 500 - waits longer before responding
                },
                "instructions": format_instructions_for_openai(agent.instructions)
            }
        }
        
        # Add voice if specified
        if agent.voice:
            session_payload["session"]["voice"] = agent.voice
        
        # Add noise reduction mode if specified
        if agent.noise_reduction_mode:
            # Convert enum to string value (e.g., NoiseReductionMode.NEAR_FIELD -> "near_field")
            noise_reduction_type = agent.noise_reduction_mode.value if hasattr(agent.noise_reduction_mode, 'value') else str(agent.noise_reduction_mode)
            session_payload["session"]["input_audio_noise_reduction"] = {
                "type": noise_reduction_type
            }
        
        # Add additional agent config if present
        if agent_config:
            for key, value in agent_config.items():
                if key not in session_payload["session"]:
                    session_payload["session"][key] = value
        
        # Log session update message in dev environment
        log_openai_websocket_message(session_payload)
        
        await openai_ws.send(json.dumps(session_payload))
        print(f"[Widget WS] OpenAI session configured for agent '{agent.name}'")
        
        # Store connection
        client_connections[websocket] = openai_ws
        
        # Create interaction record for tracking
        session_id = str(uuid.uuid4())
        interaction = Interaction(
            user_id=agent.user_id,
            openai_key_id=agent.openai_key_id,
            agent_id=agent.id,
            session_id=session_id,
            origin_domain=origin,
            status="active"
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        websocket_interactions[websocket] = interaction.id
        
        # Initialize usage tracking for this session
        websocket_usage[websocket] = {
            "audio_input_tokens": 0,
            "audio_output_tokens": 0,
            "text_input_tokens": 0,
            "text_output_tokens": 0,
            "total_tokens": 0
        }
        
        print(f"[Widget WS] Created interaction {interaction.id} for session {session_id}")
        
        # Start message forwarding tasks
        asyncio.create_task(handle_openai_messages(openai_ws, websocket))
        
        # Send connection confirmation
        await websocket.send_json({"type": "connected", "session_id": session_id})
        
        # Handle client messages
        while True:
            try:
                text = await websocket.receive_text()
                data = json.loads(text)
                action = data.get("action")
                
                if action == "audio_chunk":
                    # Forward audio to OpenAI
                    if openai_ws and openai_ws.open:
                        await openai_ws.send(json.dumps({
                            "type": "input_audio_buffer.append",
                            "audio": data.get("audio")
                        }))
                
                elif action == "commit":
                    # Commit audio and request response
                    if openai_ws and openai_ws.open:
                        commit_msg = {"type": "input_audio_buffer.commit"}
                        response_msg = {"type": "response.create"}
                        
                        # Log messages in dev environment
                        log_openai_websocket_message(commit_msg)
                        log_openai_websocket_message(response_msg)
                        
                        await openai_ws.send(json.dumps(commit_msg))
                        await openai_ws.send(json.dumps(response_msg))
                        print("[Widget WS] Committed audio & requested response")
                
                else:
                    print(f"[Widget WS] Unknown action: {action}")
                    
            except WebSocketDisconnect:
                print("[Widget WS] Client disconnected")
                break
            except Exception as e:
                print(f"[Widget WS] Error handling message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "error": str(e)
                })
    
    except Exception as e:
        print(f"[Widget WS] Exception: {e}")
        import traceback
        traceback.print_exc()
        
        # Mark interaction as error if it exists
        if websocket in websocket_interactions:
            interaction_id = websocket_interactions.get(websocket)
            try:
                interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
                if interaction:
                    interaction.status = "error"
                    interaction.error_message = str(e)
                    interaction.ended_at = datetime.utcnow()
                    db.commit()
            except:
                pass
        
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except:
            pass
    
    finally:
        # Update interaction record with end time, duration, and REAL token usage
        if websocket in websocket_interactions:
            interaction_id = websocket_interactions.pop(websocket)
            usage_data = websocket_usage.pop(websocket, None)
            
            try:
                interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
                if interaction:
                    # Use timezone-aware datetime
                    from datetime import timezone as tz
                    now = datetime.now(tz.utc)
                    interaction.ended_at = now
                    
                    # Calculate duration
                    if interaction.started_at:
                        started = interaction.started_at
                        if started.tzinfo is None:
                            started = started.replace(tzinfo=tz.utc)
                        
                        duration = (now - started).total_seconds()
                        interaction.duration_seconds = max(duration, 0)
                    
                    # Apply REAL token usage and calculate cost
                    if usage_data and usage_data.get("total_tokens", 0) > 0:
                        # Use real token counts from OpenAI
                        interaction.update_tokens(
                            audio_input=usage_data.get("audio_input_tokens", 0),
                            audio_output=usage_data.get("audio_output_tokens", 0),
                            text_input=usage_data.get("text_input_tokens", 0),
                            text_output=usage_data.get("text_output_tokens", 0)
                        )
                        print(f"[Widget WS] 💰 REAL COST: ${interaction.estimated_cost:.4f}")
                        print(f"[Widget WS] 📊 Tokens - Audio: {interaction.audio_input_tokens}in/{interaction.audio_output_tokens}out, Text: {interaction.text_input_tokens}in/{interaction.text_output_tokens}out")
                    else:
                        # Fallback: estimate based on duration if no usage data
                        # This shouldn't happen with proper OpenAI responses
                        fallback_cost = round((interaction.duration_seconds / 60) * 0.06, 4)
                        interaction.estimated_cost = fallback_cost
                        print(f"[Widget WS] ⚠️ No usage data, using fallback estimate: ${fallback_cost}")
                    
                    interaction.status = "completed"
                    db.commit()
                    print(f"[Widget WS] ✅ Completed interaction {interaction_id}, duration: {interaction.duration_seconds:.1f}s, cost: ${interaction.estimated_cost:.4f}")
            except Exception as e:
                print(f"[Widget WS] ❌ Error updating interaction: {e}")
                import traceback
                traceback.print_exc()
        
        # Cleanup
        if websocket in client_connections:
            openai_ws = client_connections.pop(websocket)
            try:
                if openai_ws and openai_ws.open:
                    await openai_ws.close()
                print("[Widget WS] Closed OpenAI connection")
            except:
                pass
        
        try:
            await websocket.close()
        except:
            pass
        finally:
            # Close database session
            db.close()


async def handle_openai_messages(openai_ws: websockets.WebSocketClientProtocol, client_ws: WebSocket):
    """Receive messages from OpenAI and forward to widget client"""
    assistant_text = ""
    
    try:
        async for msg in openai_ws:
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                continue
            
            event_type = data.get("type", "")
            
            if event_type == "conversation.item.input_audio_transcription.completed":
                transcript = data.get("transcript", "")
                if transcript:
                    await client_ws.send_json({
                        "type": "transcript_user",
                        "text": transcript
                    })
                    print(f"[Widget WS] User: {transcript}")
            
            elif event_type == "response.audio_transcript.delta":
                assistant_text += data.get("delta", "")
            
            elif event_type == "response.audio_transcript.done":
                if assistant_text:
                    await client_ws.send_json({
                        "type": "transcript_assistant",
                        "text": assistant_text
                    })
                    print(f"[Widget WS] Assistant: {assistant_text}")
                    assistant_text = ""
            
            elif event_type == "response.audio.delta":
                delta = data.get("delta")
                if delta:
                    await client_ws.send_json({
                        "type": "audio_chunk",
                        "audio": delta
                    })
            
            elif event_type == "response.done":
                await client_ws.send_json({"type": "response_done"})
                
                # Extract and accumulate token usage from OpenAI response
                response_data = data.get("response", {})
                usage = response_data.get("usage", {})
                
                if usage and client_ws in websocket_usage:
                    # Extract detailed token counts
                    input_details = usage.get("input_token_details", {})
                    output_details = usage.get("output_token_details", {})
                    
                    # Audio tokens
                    audio_input = input_details.get("audio_tokens", 0)
                    audio_output = output_details.get("audio_tokens", 0)
                    
                    # Text tokens  
                    text_input = input_details.get("text_tokens", 0)
                    text_output = output_details.get("text_tokens", 0)
                    
                    # Accumulate usage
                    websocket_usage[client_ws]["audio_input_tokens"] += audio_input
                    websocket_usage[client_ws]["audio_output_tokens"] += audio_output
                    websocket_usage[client_ws]["text_input_tokens"] += text_input
                    websocket_usage[client_ws]["text_output_tokens"] += text_output
                    websocket_usage[client_ws]["total_tokens"] += usage.get("total_tokens", 0)
                    
                    total_usage = websocket_usage[client_ws]
                    print(f"[Widget WS] 💰 Usage: audio_in={audio_input}, audio_out={audio_output}, text_in={text_input}, text_out={text_output}")
                    print(f"[Widget WS] 📊 Session total: {total_usage['total_tokens']} tokens")
                
                print("[Widget WS] Response complete")
            
            elif event_type == "input_audio_buffer.speech_started":
                await client_ws.send_json({"type": "speech_started"})
                print("[Widget WS] User started speaking")
            
            elif event_type == "input_audio_buffer.speech_stopped":
                await client_ws.send_json({"type": "speech_stopped"})
                print("[Widget WS] User stopped speaking")
            
            elif event_type == "error":
                error_msg = data.get("error", {}).get("message", "Unknown error")
                await client_ws.send_json({
                    "type": "error",
                    "error": error_msg
                })
                print(f"[Widget WS] OpenAI error: {error_msg}")
    
    except Exception as e:
        print(f"[Widget WS] Message handler error: {e}")
    finally:
        try:
            if openai_ws and openai_ws.open:
                await openai_ws.close()
        except:
            pass


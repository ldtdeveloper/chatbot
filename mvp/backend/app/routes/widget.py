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
from app.models.agent import Agent
from app.schemas import WidgetCodeResponse
from app.dependencies import get_current_user
from app.utils.encryption import decrypt_api_key
from app.config import settings
from pathlib import Path
import uuid
import json
import asyncio
import websockets
from typing import Optional, Dict
from urllib.parse import urlparse

router = APIRouter(prefix="/api/widget", tags=["widget"])

# Widget static files directory
WIDGET_DIR = Path(__file__).parent.parent.parent / "widget"


@router.get("/widget.css")
async def get_widget_css():
    """Serve widget CSS file"""
    css_file = WIDGET_DIR / "widget.css"
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
    
    # Get the OpenAI key for this agent
    api_key = db.query(OpenAIKey).filter(
        OpenAIKey.id == agent.openai_key_id,
        OpenAIKey.is_active == True
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
    active_key = db.query(OpenAIKey).filter(
        OpenAIKey.user_id == current_user.id,
        OpenAIKey.is_active == True
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
            OpenAIKey.id == agent.openai_key_id,
            OpenAIKey.is_active == True
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
        
        # Connect to OpenAI Realtime API
        ws_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
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
                    "threshold": float(agent.noise_reduction_threshold) if agent.noise_reduction_threshold else 0.5,
                    "prefix_padding_ms": agent.noise_reduction_prefix_padding_ms or 300,
                    "silence_duration_ms": agent.noise_reduction_silence_duration_ms or 500
                },
                "instructions": agent.instructions
            }
        }
        
        # Add voice if specified
        if agent.voice:
            session_payload["session"]["voice"] = agent.voice
        
        # Add additional agent config if present
        if agent_config:
            for key, value in agent_config.items():
                if key not in session_payload["session"]:
                    session_payload["session"][key] = value
        
        await openai_ws.send(json.dumps(session_payload))
        print(f"[Widget WS] OpenAI session configured for agent '{agent.name}'")
        
        # Store connection
        client_connections[websocket] = openai_ws
        
        # Start message forwarding tasks
        asyncio.create_task(handle_openai_messages(openai_ws, websocket))
        
        # Send connection confirmation
        await websocket.send_json({"type": "connected"})
        
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
                        await openai_ws.send(json.dumps({
                            "type": "input_audio_buffer.commit"
                        }))
                        await openai_ws.send(json.dumps({
                            "type": "response.create"
                        }))
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
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except:
            pass
    
    finally:
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


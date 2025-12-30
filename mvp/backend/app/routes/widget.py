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
# Track interactions for each WebSocket connection
websocket_interactions: Dict[WebSocket, int] = {}  # Maps WebSocket to Interaction ID

# Track token usage per WebSocket session (accumulated from response.done events)
websocket_usage: Dict[WebSocket, dict] = {}  # Maps WebSocket to usage data

# Track conversation transcripts per WebSocket session
websocket_transcripts: Dict[WebSocket, list] = {}  # Maps WebSocket to list of transcript messages

# Track MCP clients for each WebSocket connection
websocket_mcp_clients: Dict[WebSocket, any] = {}  # Maps WebSocket to MCP client


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
            error_str = str(e).lower()
            # Check for credit/quota related connection errors
            if any(keyword in error_str for keyword in [
                "quota", "billing", "payment", "credit", "limit", "unauthorized", "forbidden"
            ]):
                print(f"[Widget WS] ⚠️⚠️⚠️ OPENAI API CREDIT/QUOTA ERROR ON CONNECTION ⚠️⚠️⚠️")
                print(f"[Widget WS] ❌ Connection Error: {e}")
                print(f"[Widget WS] ⚠️⚠️⚠️ Please check OpenAI account billing and credits ⚠️⚠️⚠️")
            else:
                print(f"[Widget WS] OpenAI connection failed: {e}")
            
            await websocket.send_json({
                "type": "error",
                "error": "Failed to connect to OpenAI"
            })
            await websocket.close()
            return
        # Configure OpenAI session with agent settings
        agent_config = agent.agent_config if agent.agent_config else {}
        hubspot_config = None
        
        # Fixed HubSpot MCP instructions - always added when MCP is enabled
        HUBSPOT_MCP_FIXED_INSTRUCTIONS = """--- HUBSPOT CRM INTEGRATION INSTRUCTIONS ---

You have access to HubSpot CRM tools via MCP (Model Context Protocol). Your primary responsibility is to extract customer information and save it to HubSpot CRM.

CRITICAL: When interacting with users, you MUST actively listen for and extract:
- Names (first name, last name, full name)
- Phone numbers (any format: +1-xxx-xxx-xxxx, (xxx) xxx-xxxx, xxx-xxx-xxxx, etc.)
- Email addresses
- Company names
- Job titles
- Any requests for callbacks, follow-ups, or contact

WHEN TO USE HUBSPOT TOOLS:
1. IMMEDIATELY when a user provides their name, phone number, or email
2. IMMEDIATELY when a user requests a callback or follow-up
3. IMMEDIATELY when a user expresses interest in products/services
4. IMMEDIATELY when collecting any contact information

REQUIRED ACTIONS:
1. Use the appropriate HubSpot MCP tool to create or update a contact with ALL collected information
2. Include any relevant notes about the conversation or user interest
3. Always confirm with the user that their information has been saved before ending the conversation

TOOL USAGE:
- Use HubSpot MCP tools to create contacts, update existing contacts, or log interactions
- Ensure all provided information is captured accurately
- If a user provides partial information, save what you have and note what's missing"""
        
        # Load MCP config if MCP server is enabled
        if agent.enable_mcp_server:
            try:
                from app.services.integration_config_service import get_integration_config
                hubspot_config = get_integration_config(agent.id)
                if not hubspot_config:
                    print(f"[Widget WS] ⚠️ MCP: No integration config found for agent {agent.id}")
            except Exception as e:
                print(f"[Widget WS] ❌ MCP: Error getting integration config: {e}")
                hubspot_config = None

        # Prepare instructions - always add fixed HubSpot instructions if MCP is enabled
        agent_instructions = format_instructions_for_openai(agent.instructions)
        final_instructions = agent_instructions
        
        if agent.enable_mcp_server:
            # Start with fixed HubSpot MCP instructions
            mcp_instructions = HUBSPOT_MCP_FIXED_INSTRUCTIONS
            
            # Append user-provided instructions if they exist
            if hubspot_config and hubspot_config.get('instructions'):
                user_instructions = hubspot_config['instructions'].strip()
                if user_instructions:
                    mcp_instructions = f"""{HUBSPOT_MCP_FIXED_INSTRUCTIONS}

--- ADDITIONAL USER CONFIGURED INSTRUCTIONS ---
{user_instructions}"""
            
            # Merge MCP instructions with agent instructions
            final_instructions = f"""{agent_instructions}

{mcp_instructions}"""

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
                "instructions": final_instructions
            }
        }
        # Add voice if specified
        if agent.voice:
            session_payload["session"]["voice"] = agent.voice

        # Configure MCP tools if MCP server is enabled
        if agent.enable_mcp_server:
            print(f"[Widget WS] 🔧 MCP: Starting configuration for agent {agent.id}")
            
            # Check for required keys
            missing_keys = []
            if not hubspot_config:
                missing_keys.append("integration_config")
                print(f"[Widget WS] 🔧 MCP: No hubspot_config found")
            else:
                print(f"[Widget WS] 🔧 MCP: hubspot_config found")
                if not hubspot_config.get('token'):
                    missing_keys.append("token")
                    print(f"[Widget WS] 🔧 MCP: No token in hubspot_config")
                else:
                    print(f"[Widget WS] 🔧 MCP: Token present in hubspot_config")
            
            # Configure MCP tools
            try:
                has_valid_token = hubspot_config and hubspot_config.get('token')
                print(f"[Widget WS] 🔧 MCP: has_valid_token = {has_valid_token}")
                
                # Configure MCP tools according to OpenAI Realtime API documentation
                # Reference: https://platform.openai.com/docs/guides/tools-connectors-mcp
                # HubSpot cloud MCP server requires OAuth Bearer token authentication
                
                if has_valid_token:
                    token = hubspot_config.get('token')
                    is_oauth = hubspot_config.get('is_oauth', False)
                    
                    print(f"[Widget WS] 🔧 MCP: Token type - OAuth: {is_oauth}, Length: {len(token) if token else 0}")
                    
                    # HubSpot MCP server REQUIRES OAuth 2.0 - legacy tokens don't work
                    if is_oauth:
                        # MCP tool configuration - format per OpenAI Realtime API docs
                        # Reference: https://platform.openai.com/docs/guides/tools-connectors-mcp
                        Tools = [{
                            "type": "mcp",
                            "server_label": "hubspot",  # Required by OpenAI Realtime API
                            "server_url": "https://mcp.hubspot.com",  # Required by OpenAI Realtime API
                            "require_approval": "never",
                            "headers": {
                                "Authorization": f"Bearer {token}"
                            }
                        }]
                        
                        print(f"[Widget WS] 🔧 MCP: Tool configuration created:")
                        print(f"[Widget WS] 🔧 MCP: {json.dumps(Tools, indent=2)}")
                        print(f"[Widget WS] ✅ MCP: OAuth token configured")
                    else:
                        print(f"[Widget WS] ❌ MCP: Legacy token detected - HubSpot MCP requires OAuth 2.0")
                        print(f"[Widget WS] ❌ MCP: Please set up HubSpot OAuth in Agents page")
                        print(f"[Widget WS] ❌ MCP: MCP tools will NOT be added (legacy tokens don't work)")
                        # Don't add tools with legacy token - they will fail
                        Tools = []
                else:
                    print(f"[Widget WS] ⚠️ MCP: No authentication token - tools will fail")
                    # Don't add tools without authentication
                    Tools = []
                
                # Only add tools if we have a valid configuration
                if Tools:
                    session_payload["session"]["tools"] = Tools
                    print(f"[Widget WS] ✅ MCP: Tools added to session payload")
                else:
                    print(f"[Widget WS] ⚠️ MCP: No tools added to session (missing token)")
                
            except Exception as e:
                print(f"[Widget WS] ❌ MCP: Error configuring: {e}")
                import traceback
                traceback.print_exc()
                # Don't add tools if there's an error - ensure bot works without MCP
        
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
        
        # Log MCP configuration status before sending
        if "tools" in session_payload.get("session", {}):
            tools_config = session_payload['session']['tools']
            print(f"[Widget WS] 🔧 MCP: Final tools configuration ({len(tools_config)} tool(s)):")
            for i, tool in enumerate(tools_config):
                if tool.get("type") == "mcp":
                    print(f"[Widget WS] 🔧 MCP Tool {i+1}:")
                    print(f"[Widget WS] 🔧   - server_label: {tool.get('server_label')}")
                    print(f"[Widget WS] 🔧   - server_url: {tool.get('server_url')}")
                    print(f"[Widget WS] 🔧   - require_approval: {tool.get('require_approval')}")
                    if "headers" in tool:
                        has_auth = "Authorization" in tool.get("headers", {})
                        print(f"[Widget WS] 🔧   - headers: {'✅ Present (with Authorization)' if has_auth else 'Present (no Authorization)'}")
                        if has_auth:
                            auth_header = tool["headers"]["Authorization"]
                            masked_token = f"{auth_header[:20]}...{auth_header[-4:]}" if len(auth_header) > 24 else "***"
                            print(f"[Widget WS] 🔧   - Authorization: {masked_token}")
                        print(f"[Widget WS] ✅ MCP: Authentication headers present")
                    else:
                        print(f"[Widget WS] 🔧   - headers: ❌ Missing")
                        print(f"[Widget WS] ⚠️ MCP: No authentication headers")
        else:
            print(f"[Widget WS] 🔧 MCP: No tools in session payload")
        
        print(f"[Widget WS] 🔧 MCP: Sending session.update to OpenAI...")
        await openai_ws.send(json.dumps(session_payload))
        print(f"[Widget WS] ✅ MCP: Session update sent to OpenAI")
        
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
        
        # Initialize transcript storage for this session
        websocket_transcripts[websocket] = []
        
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
                    
                    # Sync to HubSpot if MCP is enabled and agent has HubSpot config
                    if agent and agent.enable_mcp_server:
                        try:
                            from app.services.integration_config_service import get_integration_config
                            from app.services.hubspot_service import sync_conversation_to_hubspot
                            
                            hubspot_config = get_integration_config(agent.id)
                            if hubspot_config and hubspot_config.get('token'):
                                # Check if using OAuth token (required for HubSpot)
                                is_oauth = hubspot_config.get('is_oauth', False)
                                if not is_oauth:
                                    interaction.hubspot_sync_status = "failed"
                                    interaction.hubspot_sync_error = "HubSpot requires OAuth 2.0 authentication. Legacy tokens are not supported. Please set up HubSpot OAuth in the Agents page."
                                    print(f"[Widget WS] ❌ HubSpot: Legacy token detected - OAuth required")
                                    print(f"[Widget WS] ❌ HubSpot: Please configure OAuth in Agents page")
                                else:
                                    # Get conversation transcript
                                    transcript_messages = websocket_transcripts.get(websocket, [])
                                    if transcript_messages:
                                        # Combine all transcript messages
                                        full_transcript = "\n".join(transcript_messages)
                                        
                                        print(f"[Widget WS] 🔄 HubSpot: Syncing conversation to HubSpot...")
                                        print(f"[Widget WS] 🔄 HubSpot: Transcript length: {len(full_transcript)} chars")
                                        print(f"[Widget WS] 🔄 HubSpot: Transcript preview: {full_transcript[:200]}...")
                                        print(f"[Widget WS] 🔄 HubSpot: Number of messages: {len(transcript_messages)}")
                                        
                                        # Sync to HubSpot
                                        contact_id, error = sync_conversation_to_hubspot(
                                            access_token=hubspot_config['token'],
                                            transcript=full_transcript,
                                            agent_name=agent.name
                                        )
                                        
                                        if contact_id:
                                            interaction.hubspot_sync_status = "success"
                                            interaction.hubspot_contact_id = contact_id
                                            print(f"[Widget WS] ✅ HubSpot: Successfully synced contact {contact_id}")
                                        else:
                                            interaction.hubspot_sync_status = "failed"
                                            interaction.hubspot_sync_error = error or "Unknown error"
                                            print(f"[Widget WS] ❌ HubSpot: Sync failed - {error}")
                                    else:
                                        # Check if we have any conversation data at all
                                        # Even if transcripts are empty, we might have partial data
                                        interaction.hubspot_sync_status = "skipped"
                                        interaction.hubspot_sync_error = "No transcripts found - conversation was empty or too short"
                                        print(f"[Widget WS] ⚠️ HubSpot: No transcripts to sync")
                                        print(f"[Widget WS] ⚠️ HubSpot: Transcript dictionary keys: {list(websocket_transcripts.keys())}")
                                        print(f"[Widget WS] ⚠️ HubSpot: This websocket in dict: {websocket in websocket_transcripts}")
                                        if websocket in websocket_transcripts:
                                            print(f"[Widget WS] ⚠️ HubSpot: Transcript list length: {len(websocket_transcripts[websocket])}")
                            else:
                                interaction.hubspot_sync_status = "skipped"
                                interaction.hubspot_sync_error = "HubSpot not configured or no OAuth token. Please set up HubSpot OAuth in the Agents page."
                                print(f"[Widget WS] ⚠️ HubSpot: Not configured for this agent or OAuth token missing")
                        except Exception as e:
                            interaction.hubspot_sync_status = "failed"
                            interaction.hubspot_sync_error = f"Error: {str(e)}"
                            print(f"[Widget WS] ❌ HubSpot: Error during sync - {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        interaction.hubspot_sync_status = "skipped"
                        interaction.hubspot_sync_error = "MCP server not enabled"
                    
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
        
        # Clean up transcript storage
        if websocket in websocket_transcripts:
            websocket_transcripts.pop(websocket)
        
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
            
            # Log session events to track MCP initialization
            if event_type in ["session.created", "session.updated", "session.updated.done"]:
                print(f"[Widget WS] 🔧 MCP: Session event: {event_type}")
                if "session" in data:
                    session_data = data.get("session", {})
                    if "tools" in session_data:
                        tools = session_data.get("tools", [])
                        print(f"[Widget WS] 🔧 MCP: Session has {len(tools)} tool(s) configured")
                        for i, tool in enumerate(tools):
                            if tool.get("type") == "mcp":
                                print(f"[Widget WS] 🔧 MCP: Tool {i+1} - {tool.get('server_label', 'unknown')} @ {tool.get('server_url', 'unknown')}")
            
            # Log ALL events from OpenAI for debugging (temporarily)
            if event_type in ["response.audio_transcript.delta", "response.audio_transcript.done", 
                             "response.audio.delta", "response.done", "response.created",
                             "conversation.item.input_audio_transcription.completed"]:
                print(f"[Widget WS] 📨 Received event: {event_type}")
                if event_type == "response.audio_transcript.delta":
                    print(f"[Widget WS] 📨 Delta text: {data.get('delta', '')}")
                elif event_type == "response.audio_transcript.done":
                    print(f"[Widget WS] 📨 Full transcript: {data.get('transcript', '')}")
                elif event_type == "response.audio.delta":
                    print(f"[Widget WS] 📨 Audio delta length: {len(data.get('delta', ''))}")
                elif event_type == "response.created":
                    response_data = data.get("response", {})
                    print(f"[Widget WS] 📨 Response created - ID: {response_data.get('id', 'N/A')}, Status: {response_data.get('status', 'N/A')}")
                    if "error" in response_data:
                        print(f"[Widget WS] ❌ Response has error: {json.dumps(response_data.get('error'), indent=2)}")
                    # Log all response events to see what's happening
                    print(f"[Widget WS] 📨 Response created full data: {json.dumps(data, indent=2)}")
            
            # Log all MCP-related events
            if "mcp" in event_type.lower() or event_type.startswith("mcp_"):
                print(f"[Widget WS] 🔧 MCP EVENT: {event_type}")
                print(f"[Widget WS] 🔧 MCP Event Data: {json.dumps(data, indent=2)}")
                
                # Specific handling for MCP tool discovery events
                if "mcp_list_tools" in event_type.lower():
                    if "in_progress" in event_type.lower():
                        print(f"[Widget WS] 🔧 MCP: Tool discovery started")
                    elif "completed" in event_type.lower():
                        print(f"[Widget WS] ✅ MCP: Tool discovery completed successfully")
                        if "tools" in data:
                            tools_list = data.get("tools", [])
                            print(f"[Widget WS] ✅ MCP: {len(tools_list)} tool(s) available")
                            for tool in tools_list:
                                print(f"[Widget WS] ✅ MCP Tool: {tool.get('name', 'unknown')} - {tool.get('description', 'No description')[:50]}")
                    elif "failed" in event_type.lower():
                        print(f"[Widget WS] ❌ MCP: Tool discovery FAILED")
                        # Log full event data to see what error information is available
                        print(f"[Widget WS] ❌ MCP: Full failed event data: {json.dumps(data, indent=2)}")
                        if "error" in data:
                            print(f"[Widget WS] ❌ MCP Error: {json.dumps(data.get('error'), indent=2)}")
                        # Check for error in different possible locations
                        if "item" in data:
                            item_data = data.get("item", {})
                            if "error" in item_data:
                                print(f"[Widget WS] ❌ MCP Item Error: {json.dumps(item_data.get('error'), indent=2)}")
                        # Check status_details
                        if "status_details" in data:
                            status_details = data.get("status_details", {})
                            print(f"[Widget WS] ❌ MCP Status Details: {json.dumps(status_details, indent=2)}")
            
            # Handle MCP tool call events
            if event_type in ["response.tool_call", "response.tool_call.done"]:
                print(f"[Widget WS] 🔧 MCP TOOL CALL: {event_type}")
                if "tool_call" in data:
                    tool_call = data.get("tool_call", {})
                    tool_name = tool_call.get("name", "unknown")
                    tool_type = tool_call.get("type", "unknown")
                    print(f"[Widget WS] 🔧 MCP: Tool '{tool_name}' (type: {tool_type})")
                    
                    # Log tool call details
                    if "arguments" in tool_call:
                        args = tool_call.get("arguments")
                        print(f"[Widget WS] 🔧 MCP: Tool arguments: {json.dumps(args, indent=2)}")
                    
                    # If tool call is done, check for results
                    if event_type == "response.tool_call.done":
                        if "result" in tool_call:
                            result = tool_call.get("result")
                            print(f"[Widget WS] ✅ MCP: Tool result: {json.dumps(result, indent=2)}")
                        if "error" in tool_call:
                            error = tool_call.get("error")
                            print(f"[Widget WS] ❌ MCP: Tool error: {json.dumps(error, indent=2)}")
            
            # Log tool call events (legacy)
            if event_type.startswith("response.tool") and event_type not in ["response.tool_call", "response.tool_call.done"]:
                print(f"[Widget WS] 🔧 TOOL CALL EVENT: {event_type}")
                if "tool_call" in data:
                    tool_call = data.get("tool_call", {})
                    tool_name = tool_call.get("name", "unknown")
                    print(f"[Widget WS] 🔧 Tool: {tool_name}")
                    if "arguments" in tool_call:
                        print(f"[Widget WS] 🔧 Arguments: {json.dumps(tool_call.get('arguments'), indent=2)}")
                if "result" in data:
                    print(f"[Widget WS] 🔧 Tool Result: {json.dumps(data.get('result'), indent=2)}")
                print(f"[Widget WS] 🔧 Full Tool Event: {json.dumps(data, indent=2)}")
            
            # Log response events that might contain tool calls
            if event_type.startswith("response.") and ("tool" in str(data).lower() or "mcp" in str(data).lower()):
                print(f"[Widget WS] 🔧 RESPONSE with tool/MCP content: {event_type}")
                # Check if there are tool calls in the response
                if "output" in data:
                    output = data.get("output", [])
                    for item in output:
                        if item.get("type") == "tool_call" or "tool" in str(item).lower():
                            print(f"[Widget WS] 🔧 Tool call detected in response output: {json.dumps(item, indent=2)}")
            
            if event_type == "conversation.item.input_audio_transcription.completed":
                transcript = data.get("transcript", "")
                if transcript:
                    await client_ws.send_json({
                        "type": "transcript_user",
                        "text": transcript
                    })
                    print(f"[Widget WS] User: {transcript}")
                    # Store user transcript
                    if client_ws in websocket_transcripts:
                        websocket_transcripts[client_ws].append(f"User: {transcript}")
            
            elif event_type == "response.audio_transcript.delta":
                assistant_text += data.get("delta", "")
            
            elif event_type == "response.audio_transcript.done":
                # Check if transcript is in the event data itself (some events include full transcript)
                transcript = data.get("transcript", "")
                if transcript:
                    assistant_text = transcript
                
                if assistant_text:
                    await client_ws.send_json({
                        "type": "transcript_assistant",
                        "text": assistant_text
                    })
                    print(f"[Widget WS] Assistant transcript: {assistant_text}")
                    # Store assistant transcript
                    if client_ws in websocket_transcripts:
                        websocket_transcripts[client_ws].append(f"Assistant: {assistant_text}")
                    assistant_text = ""
                else:
                    print(f"[Widget WS] ⚠️ response.audio_transcript.done but no transcript found")
                    print(f"[Widget WS] ⚠️ Event data keys: {list(data.keys())}")
                    print(f"[Widget WS] ⚠️ Full event: {json.dumps(data, indent=2)}")
            
            elif event_type == "response.audio.delta":
                delta = data.get("delta")
                if delta:
                    await client_ws.send_json({
                        "type": "audio_chunk",
                        "audio": delta
                    })
            
            elif event_type == "response.done":
                # Log full response data to debug why no content is generated
                response_data = data.get("response", {})
                print(f"[Widget WS] 📨 response.done - Full response data: {json.dumps(response_data, indent=2)}")
                
                # Capture assistant transcript from response.done if not already captured
                # Sometimes the full transcript is in response.done output items
                if client_ws in websocket_transcripts:
                    output = response_data.get("output", [])
                    for item in output:
                        if item.get("type") == "message" and item.get("role") == "assistant":
                            content = item.get("content", [])
                            for content_item in content:
                                # Check for audio transcript
                                if content_item.get("type") == "audio" and content_item.get("transcript"):
                                    transcript = content_item.get("transcript")
                                    if transcript:
                                        # Check if this transcript is already stored
                                        existing_transcripts = "\n".join(websocket_transcripts[client_ws])
                                        if transcript not in existing_transcripts:
                                            websocket_transcripts[client_ws].append(f"Assistant: {transcript}")
                                            print(f"[Widget WS] 📝 Captured assistant transcript from response.done: {transcript[:100]}...")
                                # Check for text content
                                elif content_item.get("type") == "text":
                                    text = content_item.get("text", "")
                                    if text:
                                        existing_transcripts = "\n".join(websocket_transcripts[client_ws])
                                        if text not in existing_transcripts:
                                            websocket_transcripts[client_ws].append(f"Assistant: {text}")
                                            print(f"[Widget WS] 📝 Captured assistant text from response.done: {text[:100]}...")
                
                # Check for errors in response
                if "error" in response_data:
                    error_info = response_data.get("error", {})
                    error_msg = error_info.get("message", "")
                    error_type = error_info.get("type", "")
                    error_code = error_info.get("code", "")
                    
                    # Check for API credit/quota related errors
                    error_msg_lower = error_msg.lower() if error_msg else ""
                    if any(keyword in error_msg_lower for keyword in [
                        "insufficient_quota", "quota", "billing", "payment", "credit", 
                        "account_limit", "rate_limit", "usage_limit", "spend_limit"
                    ]):
                        print(f"[Widget WS] ⚠️⚠️⚠️ OPENAI API CREDIT/QUOTA ERROR IN RESPONSE ⚠️⚠️⚠️")
                        print(f"[Widget WS] ❌ Error Type: {error_type}")
                        print(f"[Widget WS] ❌ Error Code: {error_code}")
                        print(f"[Widget WS] ❌ Error Message: {error_msg}")
                        print(f"[Widget WS] ❌ Full Error Data: {json.dumps(error_info, indent=2)}")
                        print(f"[Widget WS] ⚠️⚠️⚠️ Please check OpenAI account billing and credits ⚠️⚠️⚠️")
                    else:
                        print(f"[Widget WS] ❌ Response error: {json.dumps(error_info, indent=2)}")
                
                # Check response status
                status = response_data.get("status", "unknown")
                print(f"[Widget WS] 📨 Response status: {status}")
                
                # Check if response is empty (no output items) - might indicate credit/quota issue
                output_items = response_data.get("output", [])
                if status == "completed" and not output_items:
                    print(f"[Widget WS] ⚠️ Response completed but has no output items - might indicate API credit/quota issue")
                    print(f"[Widget WS] ⚠️ Full response data: {json.dumps(response_data, indent=2)}")
                
                await client_ws.send_json({"type": "response_done"})
                
                # Extract and accumulate token usage from OpenAI response
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
                error_data = data.get("error", {})
                error_msg = error_data.get("message", "Unknown error")
                error_type = error_data.get("type", "unknown")
                error_code = error_data.get("code", "unknown")
                
                # Check for API credit/quota related errors
                error_msg_lower = error_msg.lower()
                if any(keyword in error_msg_lower for keyword in [
                    "insufficient_quota", "quota", "billing", "payment", "credit", 
                    "account_limit", "rate_limit", "usage_limit", "spend_limit"
                ]):
                    print(f"[Widget WS] ⚠️⚠️⚠️ OPENAI API CREDIT/QUOTA ERROR ⚠️⚠️⚠️")
                    print(f"[Widget WS] ❌ Error Type: {error_type}")
                    print(f"[Widget WS] ❌ Error Code: {error_code}")
                    print(f"[Widget WS] ❌ Error Message: {error_msg}")
                    print(f"[Widget WS] ❌ Full Error Data: {json.dumps(error_data, indent=2)}")
                    print(f"[Widget WS] ⚠️⚠️⚠️ Please check OpenAI account billing and credits ⚠️⚠️⚠️")
                
                await client_ws.send_json({
                    "type": "error",
                    "error": error_msg
                })
                print(f"[Widget WS] OpenAI error: {error_msg} (type: {error_type}, code: {error_code})")
            
            # Handle MCP tool calls
            elif event_type == "response.tool_call":
                tool_call = data.get("tool_call", {})
                tool_name = tool_call.get("name", "unknown")
                tool_args = tool_call.get("arguments", {})
                print(f"[Widget WS] 🔧 TOOL CALL: {tool_name}")
                print(f"[Widget WS] 🔧 Tool Arguments: {json.dumps(tool_args, indent=2)}")
            
            elif event_type == "response.tool_call.done":
                tool_call = data.get("tool_call", {})
                tool_name = tool_call.get("name", "unknown")
                tool_result = data.get("result", {})
                print(f"[Widget WS] ✅ TOOL CALL COMPLETE: {tool_name}")
                print(f"[Widget WS] ✅ Tool Result: {json.dumps(tool_result, indent=2)}")
            
            elif event_type == "response.tool_calls":
                tool_calls = data.get("tool_calls", [])
                print(f"[Widget WS] 🔧 TOOL CALLS RECEIVED: {len(tool_calls)} tool(s)")
                for i, tool_call in enumerate(tool_calls):
                    print(f"[Widget WS] 🔧 Tool {i+1}: {tool_call.get('name', 'unknown')} - {json.dumps(tool_call, indent=2)}")
            
            # Log any other unhandled events (for debugging)
            else:
                # Only log if it's not a common event we're already handling
                if event_type not in ["session.created", "session.updated", "session.updated.done", 
                                     "conversation.item.created", "conversation.item.input_audio_transcription.completed",
                                     "response.audio_transcript.delta", "response.audio_transcript.done",
                                     "response.audio.delta", "response.done", "input_audio_buffer.speech_started",
                                     "input_audio_buffer.speech_stopped", "error", "response.tool_call", 
                                     "response.tool_call.done", "response.tool_calls"]:
                    # Log unhandled MCP events
                    if "mcp" in event_type.lower():
                        print(f"[Widget WS] ⚠️ MCP: Unhandled event: {event_type}")
                        print(f"[Widget WS] ⚠️ MCP: Event Data: {json.dumps(data, indent=2)}")
                        if "error" in str(data).lower() or "failed" in event_type.lower():
                            print(f"[Widget WS] ❌ MCP: Error detected in unhandled event")
    
    except Exception as e:
        print(f"[Widget WS] Message handler error: {e}")
    finally:
        try:
            if openai_ws and openai_ws.open:
                await openai_ws.close()
        except:
            pass
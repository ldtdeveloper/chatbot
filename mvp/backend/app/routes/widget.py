"""
Widget code generation routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.assistant_config import AssistantConfig
from app.models.openai_key import OpenAIKey
from app.models.agent import Agent
from app.schemas import WidgetCodeResponse
from app.dependencies import get_current_user
from app.utils.encryption import decrypt_api_key
import uuid

router = APIRouter(prefix="/api/widget", tags=["widget"])


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
    
    # Escape instructions for JavaScript
    instructions_escaped = agent.instructions.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
    
    # Generate widget code with agent configuration
    widget_code = f"""<!-- Voice Assistant Widget: {agent.name} -->
<script>
(function() {{
    const widgetId = '{widget_id}';
    const agentId = {agent_id};
    const domain = '{agent.domain}';
    const apiBaseUrl = window.location.protocol + '//' + window.location.host;
    
    // Verify domain
    const currentDomain = window.location.hostname;
    if (!currentDomain.endsWith(domain) && currentDomain !== domain) {{
        console.warn('Widget domain mismatch. Expected:', domain, 'Got:', currentDomain);
    }}
    
    // Agent configuration
    const agentConfig = {{
        instructions: '{instructions_escaped}',
        voice: '{agent.voice}',
        noiseReduction: {{
            mode: '{agent.noise_reduction_mode}',
            threshold: '{agent.noise_reduction_threshold}',
            prefixPaddingMs: {agent.noise_reduction_prefix_padding_ms},
            silenceDurationMs: {agent.noise_reduction_silence_duration_ms}
        }}
    }};
    
    console.log('Voice Assistant Widget Loaded:', widgetId, 'for Agent:', agentId);
    console.log('Agent Config:', agentConfig);
    
    // TODO: Implement widget initialization
    // - Create widget UI
    // - Connect to backend WebSocket proxy with agent configuration
    // - Handle audio input/output
    // - Display transcriptions
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


"""
Widget code generation routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.assistant_config import AssistantConfig
from app.models.openai_key import OpenAIKey
from app.models.prompt import Prompt, PromptVersion
from app.schemas import WidgetCodeResponse
from app.dependencies import get_current_user
from app.utils.encryption import decrypt_api_key
import uuid

router = APIRouter(prefix="/api/widget", tags=["widget"])


@router.get("/code", response_model=WidgetCodeResponse)
async def generate_widget_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate JavaScript code for the voice assistant widget"""
    # Get user's assistant config
    config = db.query(AssistantConfig).filter(
        AssistantConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assistant configuration not found. Please configure your assistant first."
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
    
    # Get prompt and version if configured
    prompt = None
    prompt_version = None
    if config.prompt_id:
        prompt = db.query(Prompt).filter(Prompt.id == config.prompt_id).first()
        if config.prompt_version_id:
            prompt_version = db.query(PromptVersion).filter(
                PromptVersion.id == config.prompt_version_id
            ).first()
    
    # Generate unique widget ID
    widget_id = str(uuid.uuid4())
    
    # Generate widget code
    widget_code = f"""
<!-- Voice Assistant Widget -->
<script>
(function() {{
    const widgetId = '{widget_id}';
    const apiBaseUrl = window.location.protocol + '//' + window.location.host;
    
    // Widget initialization code
    // This will connect to your backend WebSocket proxy
    // Implementation details will be added based on your backend WebSocket setup
    
    console.log('Voice Assistant Widget Loaded:', widgetId);
    
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
        "widget_id": widget_id
    }


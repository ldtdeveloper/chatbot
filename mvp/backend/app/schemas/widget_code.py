from pydantic import BaseModel
from typing import Optional

# Widget Code Generation
class WidgetCodeResponse(BaseModel):
    widget_code: str
    widget_id: str
    assistant_id: Optional[int] = None
    assistant_name: Optional[str] = None

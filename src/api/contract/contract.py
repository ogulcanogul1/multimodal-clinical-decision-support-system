from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from enum import Enum

class AgentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    FAILED = "FAILED"
    PROCESSING = "PROCESSING"

class Message(BaseModel):
    role: str  # "doctor" veya "ai"
    content: str

class AgentRequest(BaseModel):
    consultation_id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    query: str = Field(..., example="Hastanın akciğer grafisinde infiltrasyon var mı?")
    history: List[Message] = Field(default=[])
    image_url: Optional[str] = None
    pdf_url: Optional[str] = None
    patient_context: Optional[str] = None  # Yaş, cinsiyet, kronik hastalıklar vb.

class AgentResponse(BaseModel):
    consultation_id: str
    status: AgentStatus
    message_content: str  # Senin final_report alanın buraya maplenecek
    evidence_links: Dict[str, Any]
    grad_cam_url: Optional[str] = None
    feature_importance: Optional[Dict[str, float]] = None
    gatekeeper_warnings: Optional[str] = None
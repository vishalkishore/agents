from pydantic import BaseModel
from typing import Dict, List, Optional

class UserQuery(BaseModel):
    text: str
    user_id: str
    session_id: str

class AgentResponse(BaseModel):
    agent_name: str
    result: Dict
    confidence: float
    error: Optional[str] = None

class ProcessedResponse(BaseModel):
    results: List[AgentResponse]
    explanation: str
    session_id: str

class FeedbackRequest(BaseModel):
    session_id: str
    useful: bool
    feedback_text: Optional[str] = None
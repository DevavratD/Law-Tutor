from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ChatMessage(BaseModel):
    """Model for a chat message."""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class QuestionRequest(BaseModel):
    """Request model for asking a question."""
    question: str
    document_id: Optional[str] = None
    chat_history: Optional[List[ChatMessage]] = None


class Source(BaseModel):
    """Model for a source reference in a response."""
    text: str
    score: Optional[float] = None


class QuestionResponse(BaseModel):
    """Response model for a question answer."""
    answer: str
    sources: List[Source] = []
    document_id: Optional[str] = None 
from pydantic import BaseModel
from typing import Optional


class ExplanationRequest(BaseModel):
    """Request model for legal concept explanation."""
    concept: str


class ExplanationResponse(BaseModel):
    """Response model for legal concept explanation."""
    concept: str
    explanation: str 
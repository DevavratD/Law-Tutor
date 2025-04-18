from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any

from app.models.explanation import ExplanationRequest, ExplanationResponse
from app.services.llm_service import llm_service

router = APIRouter()

@router.post("/concept", response_model=ExplanationResponse)
async def explain_legal_concept(explanation_request: ExplanationRequest):
    """
    Get an explanation for a legal concept in Indian law.
    
    - **concept**: The legal concept to explain
    """
    try:
        # Generate explanation
        explanation = await llm_service.generate_legal_explanation(
            explanation_request.concept
        )
        
        return {
            "concept": explanation_request.concept,
            "explanation": explanation
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate explanation: {str(e)}"
        ) 
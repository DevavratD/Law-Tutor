from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional

from app.models.qa import QuestionRequest, QuestionResponse
from app.services.index_service import index_service
from app.services.llm_service import llm_service

router = APIRouter()

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(question_request: QuestionRequest):
    """
    Ask a question about a specific document or general legal question.
    
    - **question**: The question to ask
    - **document_id**: Optional document ID to query against
    - **chat_history**: Optional chat history for context
    """
    try:
        # Check if document_id is provided
        if question_request.document_id:
            # Query against the document
            result = await index_service.query_document(
                question_request.document_id,
                question_request.question
            )
            
            if "error" in result:
                raise HTTPException(
                    status_code=404,
                    detail=result["error"]
                )
            
            return {
                "answer": result["answer"],
                "sources": result.get("sources", []),
                "document_id": question_request.document_id
            }
        else:
            # General legal question - use LLM service directly
            answer = await llm_service.answer_legal_question(
                question_request.question,
                question_request.chat_history
            )
            
            return {
                "answer": answer,
                "sources": [],
                "document_id": None
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )

@router.post("/chat", response_model=QuestionResponse)
async def chat_interaction(
    question_request: QuestionRequest
):
    """
    Have a conversation with the legal tutor, maintaining context through chat history.
    
    - **question**: The current question or message
    - **chat_history**: List of previous messages in the conversation
    - **document_id**: Optional document ID to ground responses in
    """
    try:
        # Use the same implementation as /ask, as it already handles chat history
        return await ask_question(question_request)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat: {str(e)}"
        ) 
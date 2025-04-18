from fastapi import APIRouter, HTTPException, Body, Query
from typing import List, Dict, Any, Optional

from app.models.quiz import QuizRequest, QuizResponse, QuizList, QuizSubmission, QuizResult
from app.services.quiz_service import quiz_service
from app.services.document_service import document_service

router = APIRouter()

@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(quiz_request: QuizRequest):
    """
    Generate a quiz based on a document.
    
    - **document_id**: The unique identifier of the document
    - **num_questions**: Number of questions to generate (default: 5)
    - **difficulty**: Difficulty level (easy, medium, hard) (default: medium)
    """
    try:
        # Check if document exists
        content = await document_service.get_document_content(quiz_request.document_id)
        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID {quiz_request.document_id} not found"
            )
        
        # Generate quiz
        quiz = await quiz_service.generate_quiz(
            quiz_request.document_id,
            quiz_request.num_questions,
            quiz_request.difficulty
        )
        
        if "error" in quiz:
            raise HTTPException(
                status_code=500,
                detail=quiz["error"]
            )
        
        return quiz
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate quiz: {str(e)}"
        )

@router.get("/list", response_model=QuizList)
async def list_quizzes(document_id: Optional[str] = None):
    """
    Get a list of all generated quizzes, optionally filtered by document ID.
    
    - **document_id**: Optional document ID to filter quizzes
    """
    try:
        if document_id:
            # Get quizzes for a specific document
            quizzes = await quiz_service.get_quizzes_for_document(document_id)
        else:
            # Get all quizzes
            quizzes = await quiz_service.get_all_quizzes()
        
        return {"quizzes": quizzes}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve quizzes: {str(e)}"
        )

@router.get("/{quiz_id}", response_model=Dict[str, Any])
async def get_quiz(quiz_id: str, include_answers: bool = False):
    """
    Get a specific quiz by ID.
    
    - **quiz_id**: The unique identifier of the quiz
    - **include_answers**: Whether to include correct answers in the response
    """
    try:
        # Get quiz
        quiz = await quiz_service.get_quiz(quiz_id)
        
        if not quiz:
            raise HTTPException(
                status_code=404,
                detail=f"Quiz with ID {quiz_id} not found"
            )
        
        # Remove correct answers if not requested
        if not include_answers and "questions" in quiz:
            for question in quiz["questions"]:
                if "correct_answer" in question:
                    del question["correct_answer"]
                if "explanation" in question:
                    del question["explanation"]
        
        return quiz
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve quiz: {str(e)}"
        )

@router.post("/{quiz_id}/submit", response_model=QuizResult)
async def submit_quiz(quiz_id: str, submission: QuizSubmission):
    """
    Submit a completed quiz for evaluation.
    
    - **quiz_id**: The unique identifier of the quiz
    - **submission**: The user's answers to the quiz questions
    """
    try:
        # Validate quiz ID
        quiz = await quiz_service.get_quiz(quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=404,
                detail=f"Quiz with ID {quiz_id} not found"
            )
        
        # Check if number of answers matches number of questions
        if len(submission.answers) != len(quiz.get("questions", [])):
            raise HTTPException(
                status_code=400,
                detail=f"Number of answers ({len(submission.answers)}) does not match number of questions ({len(quiz.get('questions', []))})"
            )
        
        # Evaluate answers
        result = await quiz_service.evaluate_quiz_answers(quiz_id, submission.answers)
        
        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit quiz: {str(e)}"
        ) 
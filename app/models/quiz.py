from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class QuizRequest(BaseModel):
    """Request model for quiz generation."""
    document_id: str
    num_questions: int = Field(default=5, ge=1, le=20)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")


class QuizQuestion(BaseModel):
    """Model for a quiz question."""
    question: str
    options: List[str]
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None


class QuizResponse(BaseModel):
    """Response model for a generated quiz."""
    quiz_id: str
    document_id: str
    generated_at: str
    difficulty: str
    num_questions: int
    questions: List[QuizQuestion]


class QuizMetadata(BaseModel):
    """Metadata for a quiz."""
    quiz_id: str
    document_id: str
    generated_at: str
    difficulty: str
    num_questions: int


class QuizList(BaseModel):
    """List of quiz metadata."""
    quizzes: List[QuizMetadata]


class QuizSubmission(BaseModel):
    """Submission model for quiz answers."""
    answers: List[str]


class QuizFeedbackItem(BaseModel):
    """Feedback for a single quiz question."""
    question_number: int
    is_correct: bool
    user_answer: str
    correct_answer: str
    explanation: str


class QuizResult(BaseModel):
    """Result model for quiz evaluation."""
    quiz_id: str
    score: float
    correct_count: int
    total_questions: int
    feedback: List[QuizFeedbackItem] 
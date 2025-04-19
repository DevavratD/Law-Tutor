import os
import sys
import asyncio
from app.services.quiz_service import quiz_service

async def test_quiz_list():
    """Test the quiz list function directly"""
    print("Testing quiz_service.get_all_quizzes()")
    
    # Get all quizzes
    quizzes = await quiz_service.get_all_quizzes()
    
    print(f"Found {len(quizzes)} quizzes")
    
    # Print quiz metadata
    for i, quiz in enumerate(quizzes):
        print(f"\nQuiz {i+1}:")
        print(f"  quiz_id: {quiz.get('quiz_id')}")
        print(f"  document_id: {quiz.get('document_id')}")
        print(f"  generated_at: {quiz.get('generated_at')}")
        print(f"  difficulty: {quiz.get('difficulty')}")
        print(f"  num_questions: {quiz.get('num_questions')}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    # Check if required directories exist
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/outputs", exist_ok=True)
    os.makedirs("data/outputs/quizzes", exist_ok=True)
    
    # Run the async test
    asyncio.run(test_quiz_list()) 
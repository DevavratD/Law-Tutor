import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

from app.services.llm_service import llm_service
from app.services.document_service import document_service

# Load environment variables
load_dotenv()

# Get output directory from environment variables
OUTPUT_DIR = os.getenv("OUTPUT_FOLDER", "data/outputs")
QUIZ_DIR = os.path.join(OUTPUT_DIR, "quizzes")

# Ensure the quiz directory exists
os.makedirs(QUIZ_DIR, exist_ok=True)


class QuizService:
    """Service for generating and managing quizzes."""
    
    async def generate_quiz(self, 
                           document_id: str, 
                           num_questions: int = 5, 
                           difficulty: str = "medium") -> Dict[str, Any]:
        """
        Generate a quiz based on a document.
        
        Args:
            document_id: The unique identifier of the document
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            The generated quiz with questions, options, and correct answers
        """
        # Get document content
        content = await document_service.get_document_content(document_id)
        if not content:
            return {"error": f"Document with ID {document_id} not found"}
        
        # Generate questions using LLM service
        questions = await llm_service.generate_quiz_questions(content, num_questions, difficulty)
        
        # Create a unique quiz ID
        quiz_id = str(uuid.uuid4())
        
        # Create quiz object
        quiz = {
            "quiz_id": quiz_id,
            "document_id": document_id,
            "generated_at": datetime.now().isoformat(),
            "difficulty": difficulty,
            "num_questions": num_questions,
            "questions": questions
        }
        
        # Save the quiz
        await self.save_quiz(quiz)
        
        return quiz
    
    async def save_quiz(self, quiz: Dict[str, Any]) -> str:
        """
        Save a quiz to the quiz directory.
        
        Args:
            quiz: The quiz to save
            
        Returns:
            The path to the saved quiz file
        """
        quiz_file = os.path.join(QUIZ_DIR, f"{quiz['quiz_id']}.json")
        
        with open(quiz_file, "w", encoding="utf-8") as f:
            json.dump(quiz, f, ensure_ascii=False, indent=2)
        
        return quiz_file
    
    async def get_quiz(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a quiz by ID.
        
        Args:
            quiz_id: The unique identifier of the quiz
            
        Returns:
            The quiz, or None if not found
        """
        quiz_file = os.path.join(QUIZ_DIR, f"{quiz_id}.json")
        
        if not os.path.exists(quiz_file):
            return None
        
        with open(quiz_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    async def get_quizzes_for_document(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get all quizzes generated for a document.
        
        Args:
            document_id: The unique identifier of the document
            
        Returns:
            List of quizzes for the document
        """
        quizzes = []
        
        for filename in os.listdir(QUIZ_DIR):
            if filename.endswith(".json"):
                quiz_file = os.path.join(QUIZ_DIR, filename)
                with open(quiz_file, "r", encoding="utf-8") as f:
                    quiz = json.load(f)
                    if quiz.get("document_id") == document_id:
                        # Remove the questions for the list view to reduce size
                        quiz_summary = {
                            "quiz_id": quiz.get("quiz_id"),
                            "document_id": quiz.get("document_id"),
                            "generated_at": quiz.get("generated_at"),
                            "difficulty": quiz.get("difficulty"),
                            "num_questions": quiz.get("num_questions")
                        }
                        quizzes.append(quiz_summary)
        
        return quizzes
    
    async def get_all_quizzes(self) -> List[Dict[str, Any]]:
        """
        Get a list of all generated quizzes.
        
        Returns:
            List of quiz metadata
        """
        quizzes = []
        
        for filename in os.listdir(QUIZ_DIR):
            if filename.endswith(".json"):
                quiz_file = os.path.join(QUIZ_DIR, filename)
                with open(quiz_file, "r", encoding="utf-8") as f:
                    quiz = json.load(f)
                    # Return metadata only, not the full quiz content
                    quiz_summary = {
                        "quiz_id": quiz.get("quiz_id"),
                        "document_id": quiz.get("document_id"),
                        "generated_at": quiz.get("generated_at"),
                        "difficulty": quiz.get("difficulty"),
                        "num_questions": quiz.get("num_questions")
                    }
                    quizzes.append(quiz_summary)
        
        return quizzes
    
    async def save_quiz_results(self, 
                               quiz_id: str, 
                               user_answers: List[str], 
                               score: float) -> Dict[str, Any]:
        """
        Save a user's quiz results.
        
        Args:
            quiz_id: The unique identifier of the quiz
            user_answers: The user's answers to the quiz questions
            score: The user's score
            
        Returns:
            The saved quiz results
        """
        # Get the quiz
        quiz = await self.get_quiz(quiz_id)
        if not quiz:
            return {"error": f"Quiz with ID {quiz_id} not found"}
        
        # Create results object
        results = {
            "result_id": str(uuid.uuid4()),
            "quiz_id": quiz_id,
            "completed_at": datetime.now().isoformat(),
            "user_answers": user_answers,
            "score": score,
            "total_questions": len(quiz.get("questions", []))
        }
        
        # Save results
        results_file = os.path.join(QUIZ_DIR, f"result_{results['result_id']}.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return results
    
    async def evaluate_quiz_answers(self, 
                                   quiz_id: str, 
                                   user_answers: List[str]) -> Dict[str, Any]:
        """
        Evaluate a user's answers to a quiz.
        
        Args:
            quiz_id: The unique identifier of the quiz
            user_answers: The user's answers to the quiz questions
            
        Returns:
            The evaluation results with score and feedback
        """
        # Get the quiz
        quiz = await self.get_quiz(quiz_id)
        if not quiz:
            return {"error": f"Quiz with ID {quiz_id} not found"}
        
        # Get the questions and correct answers
        questions = quiz.get("questions", [])
        
        # Initialize results
        correct_count = 0
        feedback = []
        
        # Evaluate each answer
        for i, (question, user_answer) in enumerate(zip(questions, user_answers)):
            correct_answer = question.get("correct_answer")
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct_count += 1
            
            feedback.append({
                "question_number": i + 1,
                "is_correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "explanation": question.get("explanation", "")
            })
        
        # Calculate score
        total_questions = len(questions)
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        # Create results
        results = {
            "quiz_id": quiz_id,
            "score": score,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "feedback": feedback
        }
        
        # Save results
        await self.save_quiz_results(quiz_id, user_answers, score)
        
        return results

# Create a singleton instance
quiz_service = QuizService() 
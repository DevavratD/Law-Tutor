import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
try:
    # Try importing from langchain_groq (underscore) first
    from langchain_groq import ChatGroq
except ImportError:
    try:
        # Fallback to hyphenated import if underscore version fails
        from langchain.chat_models import ChatGroq
    except ImportError:
        # If both fail, print helpful error
        print("ERROR: Could not import ChatGroq. Please install with:")
        print("pip install git+https://github.com/langchain-ai/langchain.git@master#subdirectory=libs/partners/groq")
        ChatGroq = None

from langchain.schema.messages import HumanMessage, AIMessage, SystemMessage

# Load environment variables
load_dotenv()

class LLMService:
    """Service for interacting with LLM models."""
    
    def __init__(self):
        """Initialize LLM service with the configured model."""
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        
        # Initialize the model with minimal parameters
        if not ChatGroq:
            self.llm = None
            return
            
        # Use a try-except block for each possible parameter combination
        try:
            # Try with minimal parameters first 
            self.llm = ChatGroq(api_key=self.api_key, model=self.model_name)
        except Exception as e1:
            print(f"Error with primary initialization method: {str(e1)}")
            try:
                # Try with groq_api_key instead
                self.llm = ChatGroq(groq_api_key=self.api_key, model=self.model_name)
            except Exception as e2:
                print(f"Error with secondary initialization method: {str(e2)}")
                try:
                    # Try with model_name instead of model
                    self.llm = ChatGroq(api_key=self.api_key, model_name=self.model_name)
                except Exception as e3:
                    print(f"Error with tertiary initialization method: {str(e3)}")
                    try:
                        # Final attempt with minimal possible parameters
                        self.llm = ChatGroq()
                    except Exception as e4:
                        print(f"All initialization methods failed: {str(e4)}")
                        self.llm = None
                        print("WARNING: LLM initialization failed. Functions requiring LLM will not work.")
    
    async def generate_response(self, 
                               prompt: str, 
                               system_message: Optional[str] = None, 
                               chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Generate a response from the LLM model.
        
        Args:
            prompt: The user's query
            system_message: Optional system message to set the context
            chat_history: Optional chat history for maintaining context
            
        Returns:
            The LLM's response as a string
        """
        if not self.llm:
            return "LLM service is unavailable. Please check your configuration and API keys."
            
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append(SystemMessage(content=system_message))
        
        # Add chat history if provided
        if chat_history:
            for message in chat_history:
                if message["role"] == "user":
                    messages.append(HumanMessage(content=message["content"]))
                elif message["role"] == "assistant":
                    messages.append(AIMessage(content=message["content"]))
        
        # Add the current prompt
        messages.append(HumanMessage(content=prompt))
        
        try:
            # Generate response
            response = self.llm(messages)
            return response.content
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return f"Error: Unable to generate response. {str(e)}"
    
    async def generate_legal_explanation(self, concept: str) -> str:
        """
        Generate an explanation for a legal concept.
        
        Args:
            concept: The legal concept to explain
            
        Returns:
            Explanation of the legal concept
        """
        system_message = """You are an expert Indian law tutor. Provide clear, concise, and accurate 
        explanations of legal concepts, with references to relevant sections of Indian law where applicable.
        Ensure explanations are educational and helpful for law students."""
        
        prompt = f"Explain the following legal concept in Indian law: {concept}"
        
        return await self.generate_response(prompt, system_message)
    
    async def generate_quiz_questions(self, 
                                     content: str, 
                                     num_questions: int = 5, 
                                     difficulty: str = "medium") -> List[Dict[str, Any]]:
        """
        Generate quiz questions based on the provided content.
        
        Args:
            content: The content to generate questions from
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            List of quiz questions with options and answers
        """
        system_message = """You are an expert at creating educational quiz questions for Indian law students.
        Generate multiple-choice questions that test understanding of legal concepts, statutes, and case law.
        Each question should have four options with one correct answer."""
        
        prompt = f"""Generate {num_questions} {difficulty}-difficulty multiple-choice quiz questions based on the following content. 
        For each question, provide 4 options and indicate the correct answer.
        
        Content: {content[:3000]}  # Limit content to prevent token limits
        
        Format each question as a JSON object with the following structure:
        {{
            "question": "...",
            "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
            "correct_answer": "A",  # The letter of the correct option
            "explanation": "..."  # Brief explanation of why this is the correct answer
        }}
        
        Return the questions as a valid JSON array.
        """
        
        response = await self.generate_response(prompt, system_message)
        
        # Parse the response as JSON
        import json
        try:
            # Handle potential formatting issues
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
                
            questions = json.loads(response)
            return questions
        except json.JSONDecodeError:
            # Return a structured error if JSON parsing fails
            return [{"error": "Failed to parse LLM response as JSON", "raw_response": response}]
    
    async def answer_legal_question(self, 
                                   question: str, 
                                   chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Answer a legal question from a student.
        
        Args:
            question: The student's legal question
            chat_history: Optional chat history for context
            
        Returns:
            Answer to the legal question
        """
        system_message = """You are an expert Indian law tutor answering questions from law students.
        Provide accurate, educational, and helpful responses based on Indian law.
        Reference relevant statutes, case law, and legal principles in your answers.
        If you're unsure about any information, clearly indicate this rather than providing incorrect information."""
        
        return await self.generate_response(question, system_message, chat_history)

# Create a singleton instance
llm_service = LLMService() 
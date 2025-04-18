import streamlit as st
import requests
import json
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import tempfile

# Load environment variables
load_dotenv()

# API URL
API_URL = "http://localhost:8000/api"

# Set page configuration
st.set_page_config(
    page_title="Indian Law Tutor",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to make API requests
def api_request(endpoint, method="GET", data=None, files=None):
    url = f"{API_URL}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=data)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Request Error: {str(e)}")
        return None

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "documents" not in st.session_state:
    st.session_state.documents = []
if "current_document" not in st.session_state:
    st.session_state.current_document = None
if "quizzes" not in st.session_state:
    st.session_state.quizzes = []
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

# Sidebar navigation
st.sidebar.title("Indian Law Tutor")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1154/1154211.png", width=100)
page = st.sidebar.radio("Navigation", ["Documents", "Quizzes", "Q&A", "Legal Concepts"])

# Load documents (if needed)
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_documents():
    response = api_request("documents/list")
    if response:
        return response.get("documents", [])
    return []

# Load quizzes (if needed)
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_quizzes(document_id=None):
    if document_id:
        response = api_request(f"quizzes/list?document_id={document_id}")
    else:
        response = api_request("quizzes/list")
    
    if response:
        return response.get("quizzes", [])
    return []

# Documents page
if page == "Documents":
    st.title("Document Management")
    
    # Tabs for document operations
    doc_tab1, doc_tab2, doc_tab3 = st.tabs(["Upload", "View Documents", "Document Analysis"])
    
    with doc_tab1:
        st.header("Upload a Legal Document")
        
        uploaded_file = st.file_uploader("Choose a file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        description = st.text_input("Description (optional)")
        
        if uploaded_file is not None and st.button("Upload Document"):
            with st.spinner("Processing document..."):
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                # Upload using the API
                with open(tmp_path, "rb") as f:
                    files = {"file": (uploaded_file.name, f)}
                    data = {"description": description} if description else {}
                    response = api_request("documents/upload", method="POST", data=data, files=files)
                
                # Clean up the temporary file
                os.unlink(tmp_path)
                
                if response:
                    st.success(f"Document uploaded successfully! Document ID: {response['document_id']}")
                    st.session_state.documents = load_documents()
    
    with doc_tab2:
        st.header("Your Documents")
        
        # Refresh documents
        if st.button("Refresh Documents"):
            # Clear the cache for load_documents
            load_documents.clear()
            st.session_state.documents = load_documents()
        
        # Display documents
        documents = load_documents()
        if documents:
            for doc in documents:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write(f"**ID:** {doc['file_id']}")
                with col2:
                    if st.button("View", key=f"view_{doc['file_id']}"):
                        st.session_state.current_document = doc['file_id']
                with col3:
                    if st.button("Generate Quiz", key=f"quiz_{doc['file_id']}"):
                        st.session_state.current_document = doc['file_id']
                        st.session_state.page = "Quizzes"
                        st.rerun()
                with col4:
                    if st.button("Delete", key=f"delete_{doc['file_id']}"):
                        if api_request(f"documents/{doc['file_id']}", method="DELETE"):
                            st.success(f"Document {doc['file_id']} deleted successfully!")
                            # Clear the cache and reload documents
                            load_documents.clear()
                            st.rerun()
                st.divider()
        else:
            st.info("No documents found. Upload a document to get started.")
    
    with doc_tab3:
        st.header("Document Analysis")
        
        if st.session_state.current_document:
            # Get document content
            response = api_request(f"documents/{st.session_state.current_document}?include_content=true")
            if response and "content" in response:
                st.write(f"**Document ID:** {response['document_id']}")
                st.write(f"**Content Length:** {response['content_length']} characters")
                
                # Display a preview of the content
                st.subheader("Content Preview")
                content = response["content"]
                st.text_area("Document Content", content, height=300)
                
                # Add Q&A section
                st.subheader("Ask Questions About This Document")
                doc_question = st.text_input("Your question about this document:")
                if st.button("Ask") and doc_question:
                    with st.spinner("Generating answer..."):
                        question_data = {
                            "question": doc_question,
                            "document_id": st.session_state.current_document
                        }
                        response = api_request("qa/ask", method="POST", data=question_data)
                        if response:
                            st.write("**Answer:**")
                            st.write(response["answer"])
                            
                            if response.get("sources"):
                                st.write("**Sources:**")
                                for source in response["sources"]:
                                    st.info(source["text"])
            else:
                st.error("Failed to load document content.")
        else:
            st.info("Select a document from the 'View Documents' tab to analyze it.")

# Quizzes page
elif page == "Quizzes":
    st.title("Quizzes")
    
    # Tabs for quiz operations
    quiz_tab1, quiz_tab2, quiz_tab3 = st.tabs(["Generate Quiz", "Take Quiz", "Quiz Results"])
    
    with quiz_tab1:
        st.header("Generate a Quiz")
        
        # Document selection
        documents = load_documents()
        document_options = {doc["file_id"]: f"Document: {doc['file_id']}" for doc in documents}
        
        if document_options:
            selected_document = st.selectbox(
                "Select a document", 
                options=list(document_options.keys()),
                format_func=lambda x: document_options[x]
            )
            
            num_questions = st.slider("Number of Questions", min_value=3, max_value=20, value=5)
            difficulty = st.select_slider("Difficulty", options=["easy", "medium", "hard"], value="medium")
            
            if st.button("Generate Quiz"):
                with st.spinner("Generating quiz..."):
                    quiz_data = {
                        "document_id": selected_document,
                        "num_questions": num_questions,
                        "difficulty": difficulty
                    }
                    
                    response = api_request("quizzes/generate", method="POST", data=quiz_data)
                    
                    if response and "quiz_id" in response:
                        st.success(f"Quiz generated successfully! Quiz ID: {response['quiz_id']}")
                        st.session_state.current_quiz = response["quiz_id"]
                        # Clear the quiz cache to ensure the new quiz shows up
                        load_quizzes.clear()
                        st.session_state.quizzes = load_quizzes()
                        # Switch to take quiz tab
                        quiz_tab2.active = True
        else:
            st.info("No documents found. Upload a document to generate quizzes.")
    
    with quiz_tab2:
        st.header("Take a Quiz")
        
        # Quiz selection
        quizzes = load_quizzes()
        quiz_options = {quiz["quiz_id"]: f"Quiz: {quiz['quiz_id']} ({quiz['difficulty']}, {quiz['num_questions']} questions)" for quiz in quizzes}
        
        if quiz_options:
            selected_quiz = st.selectbox(
                "Select a quiz", 
                options=list(quiz_options.keys()),
                format_func=lambda x: quiz_options[x],
                index=0 if st.session_state.current_quiz in quiz_options else 0
            )
            
            # Load the selected quiz
            quiz_response = api_request(f"quizzes/{selected_quiz}")
            
            if quiz_response and "questions" in quiz_response:
                st.session_state.current_quiz = selected_quiz
                
                # Display quiz information
                st.write(f"**Document ID:** {quiz_response['document_id']}")
                st.write(f"**Difficulty:** {quiz_response['difficulty']}")
                st.write(f"**Questions:** {quiz_response['num_questions']}")
                
                # Initialize answers if needed
                if selected_quiz not in st.session_state.quiz_answers:
                    st.session_state.quiz_answers[selected_quiz] = [""] * len(quiz_response["questions"])
                
                # Display quiz questions
                for i, question in enumerate(quiz_response["questions"]):
                    st.subheader(f"Question {i+1}")
                    st.write(question["question"])
                    
                    # Display options as radio buttons
                    st.session_state.quiz_answers[selected_quiz][i] = st.radio(
                        f"Select an answer for question {i+1}:",
                        options=[opt.split(". ", 1)[0] for opt in question["options"]],
                        key=f"q_{selected_quiz}_{i}"
                    )
                
                # Submit button
                if st.button("Submit Quiz"):
                    with st.spinner("Evaluating answers..."):
                        # Prepare submission data
                        submission_data = {
                            "answers": st.session_state.quiz_answers[selected_quiz]
                        }
                        
                        # Submit answers
                        result = api_request(f"quizzes/{selected_quiz}/submit", method="POST", data=submission_data)
                        
                        if result:
                            st.session_state.quiz_result = result
                            # Switch to results tab
                            quiz_tab3.active = True
            else:
                st.error("Failed to load quiz questions.")
        else:
            st.info("No quizzes found. Generate a quiz first.")
    
    with quiz_tab3:
        st.header("Quiz Results")
        
        if "quiz_result" in st.session_state and st.session_state.quiz_result:
            result = st.session_state.quiz_result
            
            # Display overall results
            st.subheader("Your Score")
            st.write(f"**Score:** {result['score']:.1f}%")
            st.write(f"**Correct Answers:** {result['correct_count']}/{result['total_questions']}")
            
            # Progress bar for score
            st.progress(result['score'] / 100)
            
            # Display feedback for each question
            st.subheader("Feedback")
            for feedback in result["feedback"]:
                if feedback["is_correct"]:
                    st.success(f"Question {feedback['question_number']}: Correct! ✓")
                else:
                    st.error(f"Question {feedback['question_number']}: Incorrect ✗")
                    st.write(f"Your answer: {feedback['user_answer']}")
                    st.write(f"Correct answer: {feedback['correct_answer']}")
                
                st.write(f"**Explanation:** {feedback['explanation']}")
                st.divider()
            
            # Clear result button
            if st.button("Start New Quiz"):
                del st.session_state.quiz_result
                st.rerun()
        else:
            st.info("Take a quiz to see your results here.")

# Q&A page
elif page == "Q&A":
    st.title("Ask Questions")
    
    # Tabs for different Q&A modes
    qa_tab1, qa_tab2 = st.tabs(["General Q&A", "Document Q&A"])
    
    with qa_tab1:
        st.header("Ask General Legal Questions")
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.write(f"**You:** {message['content']}")
            else:
                st.write(f"**AI:** {message['content']}")
        
        # Input for new question
        question = st.text_input("Ask a legal question:")
        
        if st.button("Send") and question:
            # Add question to chat history
            st.session_state.chat_history.append({"role": "user", "content": question})
            
            with st.spinner("Generating answer..."):
                # Prepare request data
                request_data = {
                    "question": question,
                    "chat_history": st.session_state.chat_history[:-1]  # Exclude the current question
                }
                
                # Send request
                response = api_request("qa/chat", method="POST", data=request_data)
                
                if response:
                    # Add response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response["answer"]})
                    st.rerun()
        
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    with qa_tab2:
        st.header("Ask Questions About a Document")
        
        # Document selection
        documents = load_documents()
        document_options = {doc["file_id"]: f"Document: {doc['file_id']}" for doc in documents}
        document_options[""] = "Select a document"
        
        if len(document_options) > 1:
            selected_document = st.selectbox(
                "Select a document", 
                options=list(document_options.keys()),
                format_func=lambda x: document_options[x],
                index=0
            )
            
            if selected_document:
                # Input for document question
                doc_question = st.text_input("Ask a question about this document:")
                
                if st.button("Ask") and doc_question:
                    with st.spinner("Generating answer..."):
                        question_data = {
                            "question": doc_question,
                            "document_id": selected_document
                        }
                        response = api_request("qa/ask", method="POST", data=question_data)
                        if response:
                            st.write("**Answer:**")
                            st.write(response["answer"])
                            
                            if response.get("sources"):
                                st.write("**Sources:**")
                                for source in response["sources"]:
                                    st.info(source["text"])
        else:
            st.info("No documents found. Upload a document to ask questions about it.")

# Legal Concepts page
elif page == "Legal Concepts":
    st.title("Legal Concept Explanations")
    
    # Input for concept
    concept = st.text_input("Enter a legal concept to explain:")
    
    if st.button("Explain") and concept:
        with st.spinner("Generating explanation..."):
            explanation_data = {
                "concept": concept
            }
            response = api_request("explanations/concept", method="POST", data=explanation_data)
            
            if response:
                st.subheader(response["concept"])
                st.write(response["explanation"])
    
    # Popular concepts
    st.subheader("Popular Legal Concepts")
    popular_concepts = [
        "Habeas Corpus", 
        "Article 21 of Indian Constitution",
        "Double Jeopardy",
        "Res Judicata",
        "Stare Decisis",
        "Bail Provisions in CrPC"
    ]
    
    for concept in popular_concepts:
        if st.button(concept):
            with st.spinner(f"Generating explanation for {concept}..."):
                explanation_data = {
                    "concept": concept
                }
                response = api_request("explanations/concept", method="POST", data=explanation_data)
                
                if response:
                    st.subheader(response["concept"])
                    st.write(response["explanation"])

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Indian Law Tutor** is an AI-powered assistant for law students.
    
    Upload legal documents, generate quizzes, and get answers to your legal questions.
    """
)

if __name__ == "__main__":
    # Only run when directly executed, not when imported
    import sys
    # Check if this script is being run directly or imported elsewhere
    if sys.argv[0].endswith("streamlit_app.py") or "streamlit" in sys.argv[0]:
        st.title("Indian Law Tutor")
    # Command: streamlit run app/streamlit_app.py 
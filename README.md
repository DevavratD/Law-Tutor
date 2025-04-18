# Indian Law Tutor

An AI-powered tutoring system for Indian law students, featuring document management, Q&A functionality, quiz generation, and legal concept explanations.

## Features

- **Document Management**: Upload, view, and delete legal documents (PDF, DOCX, TXT)
- **Q&A System**: Ask questions about specific documents or general legal queries
- **Quiz Generation**: Create and take quizzes based on uploaded documents
- **Legal Concept Explanations**: Get detailed explanations of legal concepts

## Architecture

- **Backend**: FastAPI with LlamaIndex for document indexing and retrieval
- **Frontend**: Streamlit for interactive web interface
- **LLM**: Powered by Groq's Llama-3 models for natural language understanding and generation

## Project Structure

```
.
├── app/                      # Main application code
│   ├── api/                  # API endpoints
│   ├── models/               # Pydantic models
│   ├── services/             # Business logic services
│   ├── main.py               # FastAPI app entry point
│   └── streamlit_app.py      # Streamlit frontend
├── data/                     # Data storage
│   ├── uploads/              # Uploaded documents
│   └── outputs/              # Processed documents and indices
├── API_DOCUMENTATION.md      # API reference for developers
├── install.py                # Installation script
├── requirements.txt          # Python dependencies
├── run.py                    # Combined startup script (frontend + backend)
├── run_api.py                # Backend-only startup script
├── run_streamlit.py          # Frontend-only startup script
├── verify_imports.py         # Dependency verification script
└── .env                      # Environment variables
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/indian-law-tutor.git
   cd indian-law-tutor
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Run the installation script:
   ```
   python install.py
   ```

4. Create a `.env` file with your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key
   LLM_MODEL=llama-3.3-70b-versatile
   LLM_PROVIDER=groq
   UPLOAD_FOLDER=data/uploads
   OUTPUT_FOLDER=data/outputs
   ```

## Running the Application

### Combined (Frontend + Backend)
```
python run.py
```

### Backend Only
```
python run_api.py
```

### Frontend Only
```
python run_streamlit.py
```

The frontend will be available at http://localhost:8501, and the backend API at http://localhost:8000.

## Developer Integration

The system provides a comprehensive API that can be integrated with other applications. See `API_DOCUMENTATION.md` for complete API reference and integration examples.

## Requirements

- Python 3.9+
- See `requirements.txt` for Python dependencies

## License

[MIT License](LICENSE) 
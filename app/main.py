import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Indian Law Tutor API",
    description="A FastAPI backend for an AI-powered Indian Law Tutor",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import API routers
from app.api.document import router as document_router
from app.api.quiz import router as quiz_router
from app.api.qa import router as qa_router
from app.api.explanation import router as explanation_router

# Include routers
app.include_router(document_router, prefix="/api/documents", tags=["Documents"])
app.include_router(quiz_router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(qa_router, prefix="/api/qa", tags=["Q&A"])
app.include_router(explanation_router, prefix="/api/explanations", tags=["Explanations"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Indian Law Tutor API", "status": "online"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 
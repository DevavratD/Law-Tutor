from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class DocumentResponse(BaseModel):
    """Response model for document upload and processing."""
    document_id: str
    filename: str
    description: Optional[str] = None
    content_length: int
    status: str


class DocumentMetadata(BaseModel):
    """Metadata for a processed document."""
    file_id: str
    extraction_date: str
    content_length: int


class DocumentList(BaseModel):
    """List of document metadata."""
    documents: List[DocumentMetadata]


class DocumentContent(BaseModel):
    """Full content of a document."""
    document_id: str
    content: str
    content_length: int 
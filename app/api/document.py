from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import uuid
import os

from app.models.document import DocumentResponse, DocumentList
from app.services.document_service import document_service
from app.services.index_service import index_service

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """
    Upload a document file (PDF, DOCX, TXT) for processing.
    
    - **file**: The document file to upload
    - **description**: Optional description of the document
    """
    # Check file extension
    filename = file.filename
    valid_extensions = [".pdf", ".docx", ".txt"]
    file_extension = os.path.splitext(filename)[1].lower()
    
    if file_extension not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(valid_extensions)}"
        )
    
    try:
        # Save the uploaded file
        file_path = await document_service.save_uploaded_file(file.file, filename)
        
        # Extract text from the document
        text_content = await document_service.extract_text_from_file(file_path)
        
        # Generate a unique document ID
        document_id = str(uuid.uuid4())
        
        # Save the extracted text
        await document_service.save_extracted_text(document_id, text_content)
        
        # Create document index
        await index_service.create_document_index(document_id, text_content)
        
        return {
            "document_id": document_id,
            "filename": filename,
            "description": description,
            "content_length": len(text_content),
            "status": "processed"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )

@router.get("/list", response_model=DocumentList)
async def list_documents():
    """
    Get a list of all uploaded and processed documents.
    """
    try:
        # Get all documents
        documents = await document_service.get_all_documents()
        
        return {"documents": documents}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve documents: {str(e)}"
        )

@router.get("/{document_id}", response_model=Dict[str, Any])
async def get_document(document_id: str, include_content: bool = False):
    """
    Get details of a specific document by ID.
    
    - **document_id**: The unique identifier of the document
    - **include_content**: Whether to include the full document content in the response
    """
    try:
        # Get document content
        content = await document_service.get_document_content(document_id)
        
        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID {document_id} not found"
            )
        
        response = {
            "document_id": document_id,
            "content_length": len(content)
        }
        
        if include_content:
            response["content"] = content
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve document: {str(e)}"
        )

@router.delete("/{document_id}", response_model=Dict[str, str])
async def delete_document(document_id: str):
    """
    Delete a document and its associated data.
    
    - **document_id**: The unique identifier of the document to delete
    """
    try:
        # Check if document exists
        content = await document_service.get_document_content(document_id)
        
        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID {document_id} not found"
            )
        
        # Delete the document content and metadata
        success = await document_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete document {document_id}"
            )
        
        # Also delete any index for this document
        await index_service.delete_document_index(document_id)
        
        return {
            "status": "success",
            "message": f"Document with ID {document_id} has been deleted"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        ) 
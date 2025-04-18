import os
import json
import uuid
from typing import Dict, List, Optional, BinaryIO
from datetime import datetime
from dotenv import load_dotenv
import pypdf
import docx2txt

# Load environment variables
load_dotenv()

# Get upload directory from environment variables
UPLOAD_DIR = os.getenv("UPLOAD_FOLDER", "data/uploads")
OUTPUT_DIR = os.getenv("OUTPUT_FOLDER", "data/outputs")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


class DocumentService:
    """Service for handling document uploads and text extraction."""
    
    async def save_uploaded_file(self, file: BinaryIO, filename: str) -> str:
        """
        Save an uploaded file to the upload directory.
        
        Args:
            file: The file object
            filename: The original filename
            
        Returns:
            The path to the saved file
        """
        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(file.read())
        
        return file_path
    
    async def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from an uploaded document file (PDF, DOCX, TXT).
        
        Args:
            file_path: Path to the uploaded file
            
        Returns:
            Extracted text content
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == ".pdf":
            return await self._extract_text_from_pdf(file_path)
        elif file_extension == ".docx":
            return await self._extract_text_from_docx(file_path)
        elif file_extension == ".txt":
            return await self._extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        text = ""
        with open(file_path, "rb") as f:
            pdf_reader = pypdf.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    async def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file."""
        try:
            text = docx2txt.process(file_path)
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX: {str(e)}")
            return ""
    
    async def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from a TXT file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    async def save_extracted_text(self, file_id: str, text: str) -> str:
        """
        Save extracted text to a JSON file.
        
        Args:
            file_id: Unique identifier for the file
            text: Extracted text content
            
        Returns:
            Path to the saved JSON file
        """
        output_file = os.path.join(OUTPUT_DIR, f"{file_id}.json")
        
        data = {
            "file_id": file_id,
            "extraction_date": datetime.now().isoformat(),
            "content": text
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_file
    
    async def get_document_content(self, file_id: str) -> Optional[str]:
        """
        Retrieve the content of a previously processed document.
        
        Args:
            file_id: The unique identifier of the document
            
        Returns:
            The document content, or None if not found
        """
        file_path = os.path.join(OUTPUT_DIR, f"{file_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("content", "")
    
    async def get_all_documents(self) -> List[Dict]:
        """
        Get a list of all processed documents.
        
        Returns:
            List of document metadata
        """
        documents = []
        
        for filename in os.listdir(OUTPUT_DIR):
            if filename.endswith(".json"):
                file_path = os.path.join(OUTPUT_DIR, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Extract only the metadata, not the full content
                    document = {
                        "file_id": data.get("file_id"),
                        "extraction_date": data.get("extraction_date"),
                        "content_length": len(data.get("content", ""))
                    }
                    documents.append(document)
        
        return documents
        
    async def delete_document(self, file_id: str) -> bool:
        """
        Delete a document and its associated data.
        
        Args:
            file_id: The unique identifier of the document to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Get the document file path
            file_path = os.path.join(OUTPUT_DIR, f"{file_id}.json")
            
            # Check if file exists
            if not os.path.exists(file_path):
                return False
                
            # Delete the file
            os.remove(file_path)
            
            # Check if there are any uploaded files associated with this document
            # We don't know the original filename, so we can't delete it directly
            # But we can look for files in the upload directory that might be related
            # (This is a best effort cleanup)
            for filename in os.listdir(UPLOAD_DIR):
                if file_id in filename:
                    upload_path = os.path.join(UPLOAD_DIR, filename)
                    try:
                        os.remove(upload_path)
                    except Exception as e:
                        print(f"Failed to delete uploaded file {filename}: {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return False

# Create a singleton instance
document_service = DocumentService() 
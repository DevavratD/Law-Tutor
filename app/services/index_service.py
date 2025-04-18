import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Handle potential import errors with LlamaIndex
try:
    from llama_index.core import VectorStoreIndex, Document, Settings
    from llama_index.core.storage import StorageContext
    from llama_index.core.vector_stores import SimpleVectorStore
    from llama_index.llms.groq import Groq
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
except ImportError:
    # Fallback to older versions
    try:
        from llama_index import VectorStoreIndex, Document, Settings
        from llama_index.storage.storage_context import StorageContext
        from llama_index.vector_stores import SimpleVectorStore
        from llama_index.llms import Groq
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    except ImportError:
        print("Warning: Failed to import LlamaIndex modules. Please check your installation.")

# Load environment variables
load_dotenv()

# Get environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
OUTPUT_DIR = os.getenv("OUTPUT_FOLDER", "data/outputs")
INDICES_DIR = os.path.join(OUTPUT_DIR, "indices")

# Ensure the indices directory exists
os.makedirs(INDICES_DIR, exist_ok=True)


class IndexService:
    """Service for document indexing and retrieval using LlamaIndex."""
    
    def __init__(self):
        """Initialize the index service with embedding model and LLM."""
        try:
            # Initialize embedding model - without safe_serialization
            # Use a version of initialization that doesn't pass unsafe parameters
            try:
                # First try with minimal parameters
                self.embed_model = HuggingFaceEmbedding(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
            except Exception as e1:
                print(f"Error initializing embedding model with basic parameters: {str(e1)}")
                # Try again with more control, manually setting the model
                try:
                    import torch
                    from transformers import AutoModel, AutoTokenizer
                    
                    # Load model directly first
                    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
                    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
                    
                    # Then pass to the embedding class
                    self.embed_model = HuggingFaceEmbedding(
                        model_name="sentence-transformers/all-MiniLM-L6-v2",
                        model=model,
                        tokenizer=tokenizer
                    )
                except Exception as e2:
                    print(f"Error initializing embedding model with manual approach: {str(e2)}")
                    self.embed_model = None
                
            # Initialize LLM
            try:
                self.llm = Groq(
                    api_key=GROQ_API_KEY,
                    model=MODEL_NAME
                )
            except Exception as e:
                print(f"Error initializing Groq: {str(e)}")
                self.llm = None
            
            # Update global settings
            Settings.embed_model = self.embed_model
            Settings.llm = self.llm
            
            # Track document indices
            self.indices = {}
        except Exception as e:
            print(f"Error initializing IndexService: {str(e)}")
            # Create placeholders to prevent runtime errors
            self.embed_model = None
            self.llm = None
            self.indices = {}
        
    async def create_document_index(self, file_id: str, content: str) -> bool:
        """
        Create a vector index for a document.
        
        Args:
            file_id: The unique identifier of the document
            content: The text content of the document
            
        Returns:
            True if indexing was successful, False otherwise
        """
        try:
            # Create a Document object
            doc = Document(text=content, doc_id=file_id)
            
            # Create storage context with vector store
            storage_context = StorageContext.from_defaults(vector_store=SimpleVectorStore())
            
            # Create the index
            index = VectorStoreIndex.from_documents(
                [doc],
                storage_context=storage_context
            )
            
            # Save the index
            index_dir = os.path.join(INDICES_DIR, file_id)
            os.makedirs(index_dir, exist_ok=True)
            index.storage_context.persist(persist_dir=index_dir)
            
            # Save metadata
            self._save_index_metadata(file_id)
            
            # Store in memory
            self.indices[file_id] = index
            
            return True
        except Exception as e:
            print(f"Error creating index: {str(e)}")
            return False
    
    def _save_index_metadata(self, file_id: str):
        """Save index metadata to a JSON file."""
        metadata_file = os.path.join(INDICES_DIR, "metadata.json")
        
        # Read existing metadata if available
        metadata = {}
        if os.path.exists(metadata_file):
            with open(metadata_file, "r") as f:
                try:
                    metadata = json.load(f)
                except json.JSONDecodeError:
                    metadata = {}
        
        # Add or update this document
        metadata[file_id] = {
            "indexed_at": os.path.getmtime(os.path.join(INDICES_DIR, file_id)),
            "index_location": os.path.join(INDICES_DIR, file_id)
        }
        
        # Save updated metadata
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
    
    async def load_index(self, file_id: str) -> Optional[VectorStoreIndex]:
        """
        Load a document index from disk.
        
        Args:
            file_id: The unique identifier of the document
            
        Returns:
            The loaded index, or None if not found
        """
        # Check if already loaded in memory
        if file_id in self.indices:
            return self.indices[file_id]
        
        # Check if index exists on disk
        index_dir = os.path.join(INDICES_DIR, file_id)
        if not os.path.exists(index_dir):
            return None
        
        try:
            # Load from disk
            storage_context = StorageContext.from_defaults(
                persist_dir=index_dir
            )
            
            # Try multiple methods to load the index based on different LlamaIndex versions
            try:
                # Newer method (load_from_disk)
                index = VectorStoreIndex.load_from_disk(
                    storage_context=storage_context,
                    persist_dir=index_dir
                )
            except (AttributeError, TypeError):
                try:
                    # Alternative method (load)
                    index = VectorStoreIndex.load(
                        storage_context=storage_context,
                        persist_dir=index_dir
                    )
                except (AttributeError, TypeError):
                    try:
                        # Older method (from_documents with empty document list)
                        index = VectorStoreIndex.from_documents(
                            [],
                            storage_context=storage_context
                        )
                    except Exception as e:
                        print(f"All index loading methods failed: {str(e)}")
                        return None
            
            # Store in memory
            self.indices[file_id] = index
            
            return index
        except Exception as e:
            print(f"Error loading index: {str(e)}")
            return None
    
    async def query_document(self, file_id: str, query: str) -> Dict:
        """
        Query a document index.
        
        Args:
            file_id: The unique identifier of the document
            query: The search query
            
        Returns:
            The search results with sources
        """
        # Load the index
        index = await self.load_index(file_id)
        if not index:
            return {"error": f"No index found for document {file_id}"}
        
        try:
            # Create a query engine
            query_engine = index.as_query_engine(
                similarity_top_k=3
            )
            
            # Execute the query
            response = query_engine.query(query)
            
            # Format the response
            result = {
                "answer": response.response,
                "sources": []
            }
            
            # Add sources if available
            if hasattr(response, "source_nodes"):
                for source_node in response.source_nodes:
                    result["sources"].append({
                        "text": source_node.node.text,
                        "score": source_node.score if hasattr(source_node, "score") else None
                    })
            
            return result
        except Exception as e:
            print(f"Error querying document: {str(e)}")
            return {"error": f"Failed to query document: {str(e)}"}
    
    async def get_all_indexed_documents(self) -> List[str]:
        """
        Get a list of all indexed documents.
        
        Returns:
            List of document IDs that have been indexed
        """
        metadata_file = os.path.join(INDICES_DIR, "metadata.json")
        if not os.path.exists(metadata_file):
            return []
        
        with open(metadata_file, "r") as f:
            try:
                metadata = json.load(f)
                return list(metadata.keys())
            except json.JSONDecodeError:
                return []
                
    async def delete_document_index(self, file_id: str) -> bool:
        """
        Delete a document index.
        
        Args:
            file_id: The unique identifier of the document
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Remove from memory if present
            if file_id in self.indices:
                del self.indices[file_id]
            
            # Check if index exists on disk
            index_dir = os.path.join(INDICES_DIR, file_id)
            if not os.path.exists(index_dir):
                return True  # Nothing to delete
            
            # Delete the directory and all its contents
            import shutil
            shutil.rmtree(index_dir)
            
            # Update metadata
            metadata_file = os.path.join(INDICES_DIR, "metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    try:
                        metadata = json.load(f)
                        if file_id in metadata:
                            del metadata[file_id]
                            with open(metadata_file, "w") as f_write:
                                json.dump(metadata, f_write, indent=2)
                    except json.JSONDecodeError:
                        pass
            
            return True
        except Exception as e:
            print(f"Error deleting document index: {str(e)}")
            return False

# Create a singleton instance
index_service = IndexService() 
"""
Pydantic models for request and response schemas.
Enhanced with additional fields, validation, and documentation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class UploadResponse(BaseModel):
    """Response model for file upload endpoint."""
    file_id: str = Field(..., description="Unique identifier for the uploaded file")
    filename: str = Field(..., description="Original filename")
    message: str = Field(..., description="Processing status message")
    chunks_created: Optional[int] = Field(None, description="Number of document chunks created")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "file_id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "document.pdf",
                "message": "File processed successfully. 15 chunks created and indexed.",
                "chunks_created": 15,
                "file_size": 102400
            }
        }
    }


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    question: str = Field(
        ..., 
        min_length=1, 
        max_length=2000,
        description="The question to ask about the document"
    )
    file_id: str = Field(
        ..., 
        min_length=1,
        description="UUID of the uploaded file to query"
    )
    max_sources: Optional[int] = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of source documents to return"
    )
    temperature: Optional[float] = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Temperature for response generation (0=deterministic, 2=creative)"
    )
    
    @field_validator('question')
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Ensure question is not just whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError('Question cannot be empty or whitespace only')
        return stripped
    
    @field_validator('file_id')
    @classmethod
    def validate_file_id(cls, v: str) -> str:
        """Ensure file_id is not just whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError('File ID cannot be empty')
        return stripped
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "What are the main topics discussed in this document?",
                "file_id": "123e4567-e89b-12d3-a456-426614174000",
                "max_sources": 5,
                "temperature": 0.1
            }
        }
    }


class Source(BaseModel):
    """Model representing a source document chunk."""
    filename: str = Field(..., description="Name of the source file")
    page_number: Optional[int] = Field(None, description="Page number if applicable")
    content: str = Field(..., description="Preview of the source content")
    relevance_score: Optional[float] = Field(None, description="Similarity score (0-1)")
    chunk_index: Optional[int] = Field(None, description="Index of the chunk in the document")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "document.pdf",
                "page_number": 5,
                "content": "This section discusses the main findings...",
                "relevance_score": 0.92,
                "chunk_index": 12
            }
        }
    }


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str = Field(..., description="AI-generated answer to the question")
    context: str = Field(..., description="Combined context used for generating the answer")
    sources: List[Source] = Field(default_factory=list, description="Source documents used")
    model_used: Optional[str] = Field(None, description="AI model used for generation")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "The document discusses three main topics: machine learning, natural language processing, and computer vision.",
                "context": "This document contains various information about artificial intelligence...",
                "sources": [
                    {
                        "filename": "document.pdf",
                        "page_number": 1,
                        "content": "This document contains various information about AI...",
                        "relevance_score": 0.95
                    }
                ],
                "model_used": "gpt-4o-mini",
                "processing_time_ms": 1250
            }
        }
    }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    message: str = Field(..., description="Health check message")
    status: str = Field(..., description="Health status (healthy, degraded, unhealthy)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Welcome to the Multi-Modal RAG API",
                "status": "healthy"
            }
        }
    }


class VectorstoreStats(BaseModel):
    """Statistics about the vectorstore."""
    total_documents: int = Field(..., description="Total number of document chunks stored")
    status: str = Field(..., description="Vectorstore status")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total_documents": 150,
                "status": "healthy"
            }
        }
    }


class FileInfo(BaseModel):
    """Information about an uploaded file."""
    file_id: str = Field(..., description="Unique identifier for the file")
    filename: str = Field(..., description="Original filename")
    upload_path: Optional[str] = Field(None, description="Server path to the file")
    size_bytes: int = Field(..., description="File size in bytes")
    uploaded_at: Optional[str] = Field(None, description="ISO timestamp of upload")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "file_id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "document.pdf",
                "upload_path": "/data/uploads/123e4567_document.pdf",
                "size_bytes": 102400,
                "uploaded_at": "2024-01-15T10:30:00"
            }
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error code/type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "validation_error",
                "message": "The uploaded file type is not supported",
                "details": {"supported_types": [".pdf", ".docx", ".txt"]}
            }
        }
    }


class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    message: str = Field(..., description="Deletion status message")
    file_id: str = Field(..., description="ID of the deleted file")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "File deleted successfully",
                "file_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    }

"""
Pydantic models for request and response schemas.
"""

from typing import List, Optional
from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Response model for file upload endpoint."""
    file_id: str
    filename: str
    message: str


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    question: str
    file_id: str
    image_base64: Optional[str] = None


class Source(BaseModel):
    """Model representing a source document."""
    filename: str
    page_number: Optional[int]
    content: str


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str
    context: str
    sources: List[Source]


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    message: str
    status: str

"""
FastAPI routes for the Multi-Modal RAG application.
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from .models import UploadResponse, QueryRequest, QueryResponse, HealthResponse
from .logic import process_document, create_and_store_embeddings, perform_rag_query, get_vectorstore_stats
from .config import settings

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        message="Welcome to the Multi-Modal RAG API",
        status="healthy"
    )


@router.get("/health", response_model=dict)
async def health_check():
    """Detailed health check with vectorstore statistics."""
    stats = get_vectorstore_stats()
    return {
        "status": "healthy",
        "message": "Multi-Modal RAG API is running",
        "vectorstore": stats
    }


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a document file.
    
    Supports: PDF, DOCX, TXT, CSV, PNG, JPG, JPEG, DB (SQLite)
    """
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.txt', '.csv', '.png', '.jpg', '.jpeg', '.db'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}. Supported types: {', '.join(allowed_extensions)}"
            )
        
        file_id = str(uuid.uuid4())
        file_path = os.path.join(settings.uploads_path, f"{file_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            chunks = process_document(file_path, file.filename)
            
            if not chunks:
                raise HTTPException(
                    status_code=400,
                    detail="No content could be extracted from the file"
                )
            
            create_and_store_embeddings(chunks, file_id)
            
            return UploadResponse(
                file_id=file_id,
                filename=file.filename,
                message=f"File processed successfully. {len(chunks)} chunks created."
            )
            
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500,
                detail=f"Error processing file: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during file upload: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse)
async def query_api(request: QueryRequest):
    """
    Query the RAG system with text and optionally an image.
    """
    try:
        if not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )
        
        if not request.file_id.strip():
            raise HTTPException(
                status_code=400,
                detail="File ID cannot be empty"
            )
        
        response = perform_rag_query(request)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/files", response_model=List[dict])
async def list_uploaded_files():
    """List all uploaded files and their IDs."""
    try:
        files = []
        uploads_dir = Path(settings.uploads_path)
        
        if uploads_dir.exists():
            for file_path in uploads_dir.iterdir():
                if file_path.is_file():
                    # Extract file_id and original filename
                    filename = file_path.name
                    if '_' in filename:
                        file_id = filename.split('_')[0]
                        original_name = '_'.join(filename.split('_')[1:])
                        
                        files.append({
                            "file_id": file_id,
                            "filename": original_name,
                            "upload_path": str(file_path),
                            "size_bytes": file_path.stat().st_size
                        })
        
        return files
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing files: {str(e)}"
        )

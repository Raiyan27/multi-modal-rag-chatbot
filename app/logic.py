"""
Business logic for the Multi-Modal RAG application.
Handles document processing, embedding creation, and RAG pipeline.
Enhanced with improved error handling, logging, caching, and performance optimizations.
"""

import os
import io
import sqlite3
import base64
import time
import logging
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from functools import lru_cache

import pandas as pd
import pytesseract
from PIL import Image
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader
)
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

from .config import settings
from .models import QueryRequest, QueryResponse, Source

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# Caching and Singleton Patterns
# =============================================================================

_embeddings_instance: Optional[OpenAIEmbeddings] = None
_openai_client: Optional[OpenAI] = None


def get_embeddings() -> OpenAIEmbeddings:
    """
    Get or create a singleton OpenAI embeddings instance.
    
    Returns:
        OpenAIEmbeddings instance
    """
    global _embeddings_instance
    
    if _embeddings_instance is None:
        logger.info("Initializing OpenAI embeddings instance")
        _embeddings_instance = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model=settings.openai_embedding_model
        )
    
    return _embeddings_instance


def get_openai_client() -> OpenAI:
    """
    Get or create a singleton OpenAI client instance.
    
    Returns:
        OpenAI client instance
    """
    global _openai_client
    
    if _openai_client is None:
        logger.info("Initializing OpenAI client instance")
        _openai_client = OpenAI(api_key=settings.openai_api_key)
    
    return _openai_client


def get_vectorstore() -> Chroma:
    """
    Get ChromaDB vectorstore instance.
    
    Returns:
        Chroma vectorstore instance
    """
    return Chroma(
        persist_directory=settings.chroma_db_path,
        embedding_function=get_embeddings()
    )


# =============================================================================
# Text Processing
# =============================================================================

@lru_cache(maxsize=1)
def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """
    Get configured text splitter for document chunking.
    Uses caching to avoid repeated instantiation.
    
    Returns:
        RecursiveCharacterTextSplitter instance
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        is_separator_regex=False
    )


# =============================================================================
# Document Processing
# =============================================================================

def process_pdf(file_path: str, filename: str) -> List[Document]:
    """Process PDF file and return documents."""
    logger.info(f"Processing PDF: {filename}")
    loader = PyMuPDFLoader(file_path)
    return loader.load()


def process_docx(file_path: str, filename: str) -> List[Document]:
    """Process DOCX file and return documents."""
    logger.info(f"Processing DOCX: {filename}")
    loader = Docx2txtLoader(file_path)
    return loader.load()


def process_txt(file_path: str, filename: str) -> List[Document]:
    """Process TXT file and return documents."""
    logger.info(f"Processing TXT: {filename}")
    # Try multiple encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            loader = TextLoader(file_path, encoding=encoding)
            return loader.load()
        except UnicodeDecodeError:
            continue
    
    raise ValueError(f"Could not decode {filename} with any supported encoding")


def process_csv(file_path: str, filename: str) -> List[Document]:
    """Process CSV file and return documents."""
    logger.info(f"Processing CSV: {filename}")
    loader = CSVLoader(file_path)
    return loader.load()


def analyze_image_with_vision(file_path: str, filename: str) -> str:
    """
    Analyze an image using GPT Vision when OCR cannot extract text.
    
    Args:
        file_path: Path to the image file
        filename: Original filename
        
    Returns:
        Text description of the image content from GPT Vision
    """
    logger.info(f"Analyzing image with GPT Vision: {filename}")
    
    try:
        # Read and encode the image
        with open(file_path, "rb") as image_file:
            image_data = image_file.read()
        
        # Resize image if too large (max 2048px on longest side for efficiency)
        image = Image.open(file_path)
        max_size = 2048
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Save resized image to buffer
            buffer = io.BytesIO()
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background
            image.save(buffer, format="JPEG", quality=85)
            image_data = buffer.getvalue()
        
        image_base64 = base64.b64encode(image_data).decode()
        
        client = get_openai_client()
        
        prompt = """Analyze this image and provide a detailed description of its content. 
Include:
1. What type of image this is (photo, diagram, chart, screenshot, etc.)
2. Main subjects or objects in the image
3. Any text visible in the image (even if OCR couldn't detect it)
4. Key information, data, or concepts depicted
5. Any important details that would help someone understand the image without seeing it

Provide a comprehensive description that can be used for document retrieval and question answering."""

        response = client.chat.completions.create(
            model=settings.openai_vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=settings.openai_max_tokens,
            temperature=0.1
        )
        
        description = response.choices[0].message.content
        logger.info(f"GPT Vision successfully analyzed image: {filename}")
        
        return f"[Image Analysis: {filename}]\n\n{description}"
        
    except Exception as e:
        logger.error(f"Error analyzing image with GPT Vision: {str(e)}")
        # Return a fallback message if Vision API fails
        return f"[Image file: {filename}] - Unable to analyze image content. The image may contain graphics, diagrams, or visual content that could not be processed."


def process_image(file_path: str, filename: str) -> List[Document]:
    """
    Process image file using OCR first, then fall back to GPT Vision if no text found.
    
    Args:
        file_path: Path to the image file
        filename: Original filename
        
    Returns:
        List containing a single Document with extracted content
        
    Raises:
        Exception: If processing fails
    """
    logger.info(f"Processing image with OCR: {filename}")
    
    try:
        image = Image.open(file_path)
        
        # Convert to RGB if necessary for better OCR
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            if image.mode == 'RGBA':
                background.paste(image, mask=image.split()[-1])
            else:
                background.paste(image)
            image = background
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        if not text.strip():
            # OCR found no text - use GPT Vision to analyze the image
            logger.info(f"OCR found no text in image: {filename}. Falling back to GPT Vision.")
            text = analyze_image_with_vision(file_path, filename)
            vision_used = True
        else:
            logger.info(f"OCR extracted {len(text)} characters from image: {filename}")
            vision_used = False
        
        doc = Document(
            page_content=text,
            metadata={
                "source": filename,
                "type": "image",
                "ocr_processed": True,
                "vision_analyzed": vision_used
            }
        )
        return [doc]
        
    except Exception as ocr_error:
        error_str = str(ocr_error).lower()
        if "tesseract" in error_str or "not found" in error_str:
            raise Exception(
                f"Tesseract OCR is not installed or not in PATH. "
                f"Please install Tesseract to process image files. "
                f"Original error: {str(ocr_error)}"
            )
        else:
            raise Exception(f"Error processing image with OCR: {str(ocr_error)}")


def process_database(file_path: str, filename: str) -> List[Document]:
    """
    Process SQLite database file and return documents.
    
    Args:
        file_path: Path to the database file
        filename: Original filename
        
    Returns:
        List containing a single Document with database content
    """
    logger.info(f"Processing SQLite database: {filename}")
    
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            raise ValueError("Database contains no tables")
        
        all_data = []
        total_rows = 0
        
        for table_name in tables:
            table_name = table_name[0]
            
            try:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                row_count = cursor.fetchone()[0]
                total_rows += row_count
                
                # Read table data (limit to first 1000 rows for large tables)
                df = pd.read_sql_query(
                    f"SELECT * FROM [{table_name}] LIMIT 1000",
                    conn
                )
                
                csv_content = f"=== Table: {table_name} ({row_count} rows) ===\n{df.to_csv(index=False)}"
                all_data.append(csv_content)
                
            except Exception as table_error:
                logger.warning(f"Error reading table {table_name}: {str(table_error)}")
                all_data.append(f"=== Table: {table_name} (error reading) ===")
        
        conn.close()
        
        combined_content = "\n\n".join(all_data)
        
        doc = Document(
            page_content=combined_content,
            metadata={
                "source": filename,
                "type": "database",
                "tables_count": len(tables),
                "total_rows": total_rows
            }
        )
        
        logger.info(f"Processed database with {len(tables)} tables and {total_rows} total rows")
        return [doc]
        
    except Exception as e:
        raise Exception(f"Error processing database: {str(e)}")


def process_document(file_path: str, filename: str) -> List[Document]:
    """
    Process a document based on its file extension and return chunks.
    
    Args:
        file_path: Path to the uploaded file
        filename: Original filename
        
    Returns:
        List of Document objects with text chunks
        
    Raises:
        Exception: If processing fails
    """
    start_time = time.time()
    file_extension = Path(filename).suffix.lower()
    
    logger.info(f"Starting document processing: {filename} (type: {file_extension})")
    
    # Map extensions to processing functions
    processors = {
        '.pdf': process_pdf,
        '.docx': process_docx,
        '.txt': process_txt,
        '.csv': process_csv,
        '.png': process_image,
        '.jpg': process_image,
        '.jpeg': process_image,
        '.db': process_database
    }
    
    processor = processors.get(file_extension)
    
    if processor is None:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    try:
        # Process document
        documents = processor(file_path, filename)
        
        # Add common metadata
        for doc in documents:
            doc.metadata["filename"] = filename
            doc.metadata["file_extension"] = file_extension
        
        # Split into chunks
        text_splitter = get_text_splitter()
        chunks = text_splitter.split_documents(documents)
        
        # Add chunk indices
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = len(chunks)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Document processing complete: {filename} -> {len(chunks)} chunks in {elapsed_time:.2f}s")
        
        return chunks
        
    except Exception as e:
        logger.error(f"Error processing {filename}: {str(e)}")
        raise Exception(f"Error processing {filename}: {str(e)}")


# =============================================================================
# Embedding and Storage
# =============================================================================

def create_and_store_embeddings(docs: List[Document], file_id: str) -> int:
    """
    Create embeddings for documents and store them in ChromaDB.
    
    Args:
        docs: List of Document objects
        file_id: Unique identifier for the file
        
    Returns:
        Number of documents stored
        
    Raises:
        Exception: If embedding creation or storage fails
    """
    start_time = time.time()
    logger.info(f"Creating embeddings for {len(docs)} documents (file_id: {file_id})")
    
    try:
        # Add file_id to metadata
        for doc in docs:
            doc.metadata["file_id"] = file_id
        
        # Get vectorstore and add documents
        vectorstore = get_vectorstore()
        vectorstore.add_documents(docs)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Embeddings created and stored: {len(docs)} documents in {elapsed_time:.2f}s")
        
        return len(docs)
        
    except Exception as e:
        logger.error(f"Error creating embeddings: {str(e)}")
        raise Exception(f"Error creating embeddings: {str(e)}")


def delete_document_embeddings(file_id: str) -> bool:
    """
    Delete all embeddings associated with a file_id.
    
    Args:
        file_id: Unique identifier for the file
        
    Returns:
        True if deletion was successful
        
    Raises:
        Exception: If deletion fails
    """
    logger.info(f"Deleting embeddings for file_id: {file_id}")
    
    try:
        vectorstore = get_vectorstore()
        collection = vectorstore._collection
        
        # Get IDs of documents with matching file_id
        results = collection.get(
            where={"file_id": file_id},
            include=[]
        )
        
        if results['ids']:
            collection.delete(ids=results['ids'])
            logger.info(f"Deleted {len(results['ids'])} embeddings for file_id: {file_id}")
        else:
            logger.warning(f"No embeddings found for file_id: {file_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error deleting embeddings: {str(e)}")
        raise Exception(f"Error deleting embeddings: {str(e)}")


# =============================================================================
# Query Processing
# =============================================================================


def handle_text_query(
    question: str,
    context: str,
    temperature: float = 0.1
) -> str:
    """
    Handle text-only query using GPT-4o-mini.
    
    Args:
        question: User's question
        context: Retrieved document context
        temperature: Response generation temperature
        
    Returns:
        Generated answer
    """
    logger.info("Processing text query with GPT-4o-mini")
    
    client = get_openai_client()
    
    system_prompt = """You are an expert assistant that provides accurate, clear, and concise answers based strictly on the provided context.

Guidelines:
1. Base your answers ONLY on the provided context
2. If the context doesn't contain enough information, clearly state this
3. Cite specific parts of the context when relevant
4. Structure your response clearly with bullet points if appropriate
5. Do not make up information or use external knowledge
6. If asked for opinions or analysis, base them solely on the context"""

    user_prompt = f"""Context from the document:
{context}

Question: {question}

Please provide a comprehensive answer based on the context above."""

    response = client.chat.completions.create(
        model=settings.openai_mini_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=settings.openai_max_tokens,
        temperature=temperature
    )
    
    return response.choices[0].message.content


def perform_rag_query(query_request: QueryRequest) -> QueryResponse:
    """
    Perform RAG query and return response.
    
    Args:
        query_request: Query request object with question and file_id
        
    Returns:
        QueryResponse with answer, context, and sources
        
    Raises:
        Exception: If query processing fails
    """
    start_time = time.time()
    logger.info(f"Performing RAG query for file_id: {query_request.file_id}")
    
    try:
        # Get vectorstore and search for relevant documents
        vectorstore = get_vectorstore()
        
        max_sources = query_request.max_sources or 5
        temperature = query_request.temperature or 0.1
        
        # Perform similarity search with scores
        docs_with_scores = vectorstore.similarity_search_with_score(
            query_request.question,
            k=max_sources,
            filter={"file_id": query_request.file_id}
        )
        
        if not docs_with_scores:
            logger.warning(f"No documents found for file_id: {query_request.file_id}")
            return QueryResponse(
                answer="No relevant documents found for this query. Please ensure you have uploaded and processed a document with this file ID.",
                context="",
                sources=[],
                model_used="none",
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Extract documents and build context
        docs = [doc for doc, score in docs_with_scores]
        context = "\n\n---\n\n".join([doc.page_content for doc in docs])
        
        # Build sources list with relevance scores
        sources = []
        for doc, score in docs_with_scores:
            # ChromaDB returns distance, convert to similarity (lower distance = higher similarity)
            relevance_score = max(0, 1 - score) if score < 1 else 1 / (1 + score)
            
            source = Source(
                filename=doc.metadata.get("filename", "Unknown"),
                page_number=doc.metadata.get("page", None),
                content=doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                relevance_score=round(relevance_score, 3),
                chunk_index=doc.metadata.get("chunk_index", None)
            )
            sources.append(source)
        
        # Generate answer using text query (all documents are now text-based)
        answer = handle_text_query(
            query_request.question,
            context,
            temperature
        )
        model_used = settings.openai_mini_model
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.info(f"RAG query complete: {len(sources)} sources, {processing_time_ms}ms")
        
        return QueryResponse(
            answer=answer,
            context=context,
            sources=sources,
            model_used=model_used,
            processing_time_ms=processing_time_ms
        )
        
    except Exception as e:
        logger.error(f"Error performing RAG query: {str(e)}")
        raise Exception(f"Error performing RAG query: {str(e)}")


# =============================================================================
# Statistics and Monitoring
# =============================================================================

def get_vectorstore_stats() -> Dict[str, Any]:
    """
    Get statistics about the vectorstore.
    
    Returns:
        Dictionary with vectorstore statistics
    """
    try:
        vectorstore = get_vectorstore()
        collection = vectorstore._collection
        count = collection.count()
        
        # Try to get unique file count
        try:
            all_metadata = collection.get(include=["metadatas"])
            unique_files = set()
            for metadata in all_metadata.get("metadatas", []):
                if metadata and "file_id" in metadata:
                    unique_files.add(metadata["file_id"])
            
            return {
                "total_documents": count,
                "unique_files": len(unique_files),
                "status": "healthy"
            }
        except:
            return {
                "total_documents": count,
                "status": "healthy"
            }
        
    except Exception as e:
        logger.error(f"Error getting vectorstore stats: {str(e)}")
        return {
            "total_documents": 0,
            "status": f"error: {str(e)}"
        }

"""
Business logic for the Multi-Modal RAG application.
Handles document processing, embedding creation, and RAG pipeline.
"""

import os
import sqlite3
import base64
from typing import List, Optional
from pathlib import Path

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


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """Get configured text splitter for document chunking."""
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )


def process_document(file_path: str, filename: str) -> List[Document]:
    """
    Process a document based on its file extension and return chunks.
    
    Args:
        file_path: Path to the uploaded file
        filename: Original filename
        
    Returns:
        List of Document objects with text chunks
    """
    file_extension = Path(filename).suffix.lower()
    documents = []
    
    try:
        if file_extension == '.pdf':
            loader = PyMuPDFLoader(file_path)
            documents = loader.load()
            
        elif file_extension == '.docx':
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            
        elif file_extension == '.txt':
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            
        elif file_extension == '.csv':
            loader = CSVLoader(file_path)
            documents = loader.load()
            
        elif file_extension in ['.png', '.jpg', '.jpeg']:
            try:
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image)
                if not text.strip():
                    text = f"Image file: {filename} (OCR found no text content)"
                doc = Document(
                    page_content=text,
                    metadata={"source": filename, "type": "image"}
                )
                documents = [doc]
            except Exception as ocr_error:
                if "tesseract" in str(ocr_error).lower():
                    raise Exception(
                        f"Tesseract OCR is not installed. To process image files, please:\n"
                        f"1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                        f"2. Install it and add to your PATH\n"
                        f"3. Restart your application\n\n"
                        f"Alternative: Use non-image files for now (PDF, DOCX, TXT, CSV)"
                    )
                else:
                    raise Exception(f"Error processing image with OCR: {str(ocr_error)}")
            
        elif file_extension == '.db':
            # Process SQLite database
            conn = sqlite3.connect(file_path)
            
            # Get all table names
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            all_data = []
            for table_name in tables:
                table_name = table_name[0]
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                csv_content = f"Table: {table_name}\n{df.to_csv(index=False)}"
                all_data.append(csv_content)
            
            conn.close()
            
            # Create document from all tables
            combined_content = "\n\n".join(all_data)
            doc = Document(
                page_content=combined_content,
                metadata={"source": filename, "type": "database"}
            )
            documents = [doc]
            
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        for doc in documents:
            doc.metadata["filename"] = filename
            
        text_splitter = get_text_splitter()
        chunks = text_splitter.split_documents(documents)
        
        return chunks
        
    except Exception as e:
        raise Exception(f"Error processing {filename}: {str(e)}")


def create_and_store_embeddings(docs: List[Document], file_id: str) -> None:
    """
    Create embeddings for documents and store them in ChromaDB.
    
    Args:
        docs: List of Document objects
        file_id: Unique identifier for the file
    """
    try:
        embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model="text-embedding-3-small"
        )
        
        for doc in docs:
            doc.metadata["file_id"] = file_id
        
        vectorstore = Chroma(
            persist_directory=settings.chroma_db_path,
            embedding_function=embeddings
        )
        
        vectorstore.add_documents(docs)
        vectorstore.persist()
        
    except Exception as e:
        raise Exception(f"Error creating embeddings: {str(e)}")


def handle_multimodal_query(question: str, image_base64: str, context_docs: List[Document]) -> str:
    """
    Handle multimodal query using GPT-4 Vision.
    
    Args:
        question: User's question
        image_base64: Base64 encoded image
        context_docs: Relevant context documents
        
    Returns:
        Generated answer
    """
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        
        context = "\n\n".join([doc.page_content for doc in context_docs])
        
        prompt = f"""Answer the question based on the following context and the provided image:

Context:
{context}

Question: {question}

Please provide a comprehensive answer based on both the text context and the image content."""

        # Prepare messages for GPT-4 Vision
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
        
        # Call GPT-4 Vision
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Error in multimodal query: {str(e)}")


def perform_rag_query(query_request: QueryRequest) -> QueryResponse:
    """
    Perform RAG query and return response.
    
    Args:
        query_request: Query request object
        
    Returns:
        Query response with answer and sources
    """
    try:
        embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model="text-embedding-3-small"
        )
        
        vectorstore = Chroma(
            persist_directory=settings.chroma_db_path,
            embedding_function=embeddings
        )
        
        docs = vectorstore.similarity_search(
            query_request.question,
            k=5,
            filter={"file_id": query_request.file_id}
        )
        
        if not docs:
            return QueryResponse(
                answer="No relevant documents found for this query.",
                context="",
                sources=[]
            )
        
        context = "\n\n".join([doc.page_content for doc in docs])
        sources = []
        
        for doc in docs:
            source = Source(
                filename=doc.metadata.get("filename", "Unknown"),
                page_number=doc.metadata.get("page", None),
                content=doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            )
            sources.append(source)
        
        if query_request.image_base64:
            answer = handle_multimodal_query(
                query_request.question,
                query_request.image_base64,
                docs
            )
        else:
            client = OpenAI(api_key=settings.openai_api_key)
            
            prompt = f"""Answer the question based only on the following context:

{context}

Question: {query_request.question}

Provide a comprehensive and accurate answer based solely on the context provided."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert assistant that provides accurate, clear, and concise answers strictly based on the provided context. Do not use external knowledge or make assumptions. If the answer is not explicitly found in the context, respond with 'The context does not provide enough information to answer this question.'"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            answer = response.choices[0].message.content
        
        return QueryResponse(
            answer=answer,
            context=context,
            sources=sources
        )
        
    except Exception as e:
        raise Exception(f"Error performing RAG query: {str(e)}")


def get_vectorstore_stats() -> dict:
    """Get statistics about the vectorstore."""
    try:
        embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model="text-embedding-3-small"
        )
        
        vectorstore = Chroma(
            persist_directory=settings.chroma_db_path,
            embedding_function=embeddings
        )
        
        collection = vectorstore._collection
        count = collection.count()
        
        return {
            "total_documents": count,
            "status": "healthy"
        }
        
    except Exception as e:
        return {
            "total_documents": 0,
            "status": f"error: {str(e)}"
        }

"""
Configuration module for the Multi-Modal RAG application.
Loads environment variables using pydantic-settings and python-dotenv.
Enhanced with additional configuration options and validation.
"""

import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be configured via environment variables or .env file.
    """
    
    # Required settings
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for embeddings and chat completions"
    )
    
    # Storage paths
    chroma_db_path: str = Field(
        default="./data/chroma_db",
        description="Path to ChromaDB persistent storage"
    )
    uploads_path: str = Field(
        default="./data/uploads",
        description="Path for uploaded file storage"
    )
    
    # API Configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="Host to bind the API server"
    )
    api_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Port for the API server"
    )
    
    # Document Processing
    max_file_size_mb: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum file size in MB"
    )
    chunk_size: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Text chunk size for document splitting"
    )
    chunk_overlap: int = Field(
        default=200,
        ge=0,
        le=500,
        description="Overlap between text chunks"
    )
    
    # RAG Configuration
    default_max_sources: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Default number of source documents to retrieve"
    )
    default_temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Default temperature for LLM responses"
    )
    
    # Model Configuration
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model to use"
    )
    chat_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI chat model for text queries"
    )
    vision_model: str = Field(
        default="gpt-4o",
        description="OpenAI model for vision queries"
    )
    
    # Debug/Development
    debug_mode: bool = Field(
        default=False,
        description="Enable debug mode for verbose logging"
    )
    
    @field_validator('openai_api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate OpenAI API key is not empty or placeholder."""
        if not v or v == "your_openai_api_key_here" or v.startswith("your_"):
            raise ValueError(
                "OPENAI_API_KEY is not set or is still a placeholder. "
                "Please set a valid OpenAI API key in your .env file."
            )
        if not v.startswith("sk-"):
            logger.warning(
                "OpenAI API key doesn't start with 'sk-'. "
                "This may not be a valid API key format."
            )
        return v
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra environment variables
    }


# Initialize global settings instance
try:
    settings = Settings()
    logger.info("Configuration loaded successfully")
    
    if settings.debug_mode:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
        
except Exception as e:
    logger.error(f"Failed to load configuration: {str(e)}")
    raise


# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        settings.chroma_db_path,
        settings.uploads_path
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")


# Create directories on module load
ensure_directories()

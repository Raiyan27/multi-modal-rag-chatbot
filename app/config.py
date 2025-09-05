"""
Configuration module for the Multi-Modal RAG application.
Loads environment variables using pydantic-settings and python-dotenv.
"""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    openai_api_key: str
    chroma_db_path: str = "./data/chroma_db"
    uploads_path: str = "./data/uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.chroma_db_path, exist_ok=True)
os.makedirs(settings.uploads_path, exist_ok=True)

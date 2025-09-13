from pydantic import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Database
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    chroma_collection_name: str = "loan_products"
    
    # AI Settings
    embedding_model: str = "all-MiniLM-L6-v2"
    anthropic_model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 4000
    temperature: float = 0.1
    
    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_retrieved_docs: int = 10
    similarity_threshold: float = 0.7
    
    # Recommendation Settings
    max_recommendations: int = 3
    min_confidence_score: float = 60.0
    high_confidence_threshold: float = 85.0
    
    # Application
    app_name: str = "AI Loan Recommender"
    app_version: str = "1.0.0"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Directories
    data_dir: str = "./data"
    raw_data_dir: str = "./data/raw"
    processed_data_dir: str = "./data/processed"
    
    class Config:
        env_file = ".env"

settings = Settings()
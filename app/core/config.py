"""
Configuration settings for the personalized learning system
"""

from pydantic import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # App configuration
    APP_NAME: str = "AI Personalized Learning System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./learning_system.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI/ML Configuration
    MODEL_PATH: str = "./models"
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    
    # Learning Configuration
    DIFFICULTY_LEVELS: list = ["beginner", "intermediate", "advanced"]
    LEARNING_STYLES: list = ["visual", "auditory", "kinesthetic", "reading_writing"]
    
    class Config:
        env_file = ".env"


settings = Settings()
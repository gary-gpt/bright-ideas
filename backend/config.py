"""
Application configuration management.
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database settings
    database_url: str = "postgresql://localhost:5432/bright_ideas"
    
    # OpenAI settings
    openai_api_key: str
    openai_model: str = "gpt-4o"
    
    # Application settings
    environment: str = "development"
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:5173"]
    
    # API settings
    api_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
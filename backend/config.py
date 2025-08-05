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
    cors_origins: List[str] = [
        "http://localhost:5173",
        "https://bright-ideas.onrender.com"
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override CORS origins from environment variable if provided
        import os
        cors_env = os.getenv('CORS_ORIGINS')
        if cors_env:
            self.cors_origins = [origin.strip() for origin in cors_env.split(',')]
        
        # Force production CORS origins in production environment
        if os.getenv('ENVIRONMENT') == 'production':
            self.cors_origins = [
                "http://localhost:5173",
                "https://bright-ideas.onrender.com"
            ]
    
    # API settings
    api_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
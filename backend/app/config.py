from pydantic_settings import BaseSettings
from typing import Optional
import secrets
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Wanderlog AI France"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database - Handle both Heroku and local URLs
    DATABASE_URL: str = os.getenv("DATABASE_URL", "").replace("postgres://", "postgresql://") if os.getenv("DATABASE_URL") else ""
    
    # Redis - Handle both Heroku and local URLs
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # API Keys
    ANTHROPIC_API_KEY: str
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - Allow Heroku apps
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000", 
        "http://localhost:8000",
        "https://*.herokuapp.com"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
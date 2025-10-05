import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API.Bible Configuration
    bible_api_key: str = os.getenv("BIBLE_API_KEY", "")
    bible_api_base_url: str = os.getenv("BIBLE_API_BASE_URL", "https://api.scripture.api.bible/v1")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./faith_dive.db")
    
    # Application Configuration
    app_name: str = os.getenv("APP_NAME", "Faith Dive")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # API Configuration
    api_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"

settings = Settings()
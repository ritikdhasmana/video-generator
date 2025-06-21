from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Hugging Face (primary - free)
    HUGGINGFACE_API_KEY: str = ""
    HUGGINGFACE_MODEL: str = "meta-llama/Llama-3.1-8B-Instruct"
    
    # Storage
    STORAGE_BASE_PATH: str = "./storage"
    STORAGE_VIDEO_PATH: str = "./storage/videos"
    STORAGE_IMAGE_PATH: str = "./storage/images"
    
    # Video Processing
    DEFAULT_VIDEO_FORMAT: str = "mp4"
    DEFAULT_DURATION: int = 30
    DEFAULT_ASPECT_RATIO: str = "16:9"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Handle CORS_ORIGINS as comma-separated string from env
        if isinstance(self.CORS_ORIGINS, str):
            self.CORS_ORIGINS = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

settings = Settings() 
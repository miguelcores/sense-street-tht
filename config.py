from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://username:password@localhost:5432/chatapi"
    supabase_url: str = ""
    supabase_key: str = ""
    
    # File handling
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [".json", ".csv"]
    
    # Processing
    processing_delay: int = 5  # Simulate processing time in seconds
    
    # API
    api_key_header: str = "X-API-Key"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
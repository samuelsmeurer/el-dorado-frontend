from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/eldorado_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # RapidAPI ScrapTik
    rapidapi_key: str = "your_rapidapi_key_here"
    rapidapi_host: str = "scraptik.p.rapidapi.com"
    
    # OpenAI
    openai_api_key: str = "your_openai_api_key_here"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # El Dorado Settings
    eldorado_mention: str = "@El Dorado P2P"
    sync_video_count: int = 20
    
    # App
    app_name: str = "El Dorado Influencer API"
    version: str = "1.0.0"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
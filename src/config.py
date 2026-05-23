from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Babel-Zilla"
    
    # Mi memoria (PostgreSQL)
    DATABASE_URL: str
    
    # Mi IA (Google Cloud)
    GOOGLE_PROJECT_ID: str
    GOOGLE_LOCATION: str = "us-central1"
    
    # Puerto dinámico para la nube
    PORT: int = 8000

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
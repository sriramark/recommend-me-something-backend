"""Application configuration management."""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseSettings, validator
from dotenv import load_dotenv


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    app_name: str = "Recommend Me Something API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database Configuration
    database_url: Optional[str] = None

    # External API Keys
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    tmdb_api_key: Optional[str] = None
    youtube_data_api_key: Optional[str] = None

    # CORS Configuration
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    cors_allow_credentials: bool = True

    # API Rate Limiting
    rate_limit_per_minute: int = 60

    # OpenAI Configuration
    openai_model: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.7
    openai_max_tokens: Optional[int] = None

    @validator("database_url", pre=True)
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL environment variable is required")
        return v

    @validator("openai_api_key", pre=True)
    def validate_openai_api_key(cls, v):
        if not v:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    # Load environment variables from .env file
    base_dir = Path(__file__).resolve().parent.parent
    load_dotenv(os.path.join(base_dir, ".env"))

    return Settings(
        database_url=os.getenv("DATABASE_URL"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        tmdb_api_key=os.getenv("TMDB_API_KEY"),
        youtube_data_api_key=os.getenv("YOUTUBE_DATA_API_KEY"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )


# Global settings instance
settings = get_settings()

"""Dependency injection and database setup."""

from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.services import (
    BookService,
    GoogleBooksService,
    MovieService,
    TMDBService,
    YouTubeService,
    OpenAIService,
)


def get_db() -> Generator[Session, None, None]:
    """Get database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_openai_service() -> OpenAIService:
    """Get OpenAI service dependency."""
    return OpenAIService()


def get_google_books_service() -> GoogleBooksService:
    """Get Google Books service dependency."""
    return GoogleBooksService()


def get_book_service() -> BookService:
    """Get Book service dependency."""
    google_books_service = get_google_books_service()
    return BookService(google_books_service)


def get_tmdb_service() -> TMDBService:
    """Get TMDB service dependency."""
    return TMDBService()


def get_youtube_service() -> YouTubeService:
    """Get YouTube service dependency."""
    return YouTubeService()


def get_movie_service() -> MovieService:
    """Get Movie service dependency."""
    tmdb_service = get_tmdb_service()
    youtube_service = get_youtube_service()
    return MovieService(tmdb_service, youtube_service)


# Create database tables
models.Base.metadata.create_all(bind=engine)

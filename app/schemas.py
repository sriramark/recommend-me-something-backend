"""Pydantic schemas for request/response models."""

from typing import Optional, List
from pydantic import BaseModel, Field


class BookBase(BaseModel):
    """Base book schema."""

    title: str = Field(..., description="Book title", min_length=1, max_length=255)
    author: Optional[str] = Field(None, description="Book author")
    cover_image_url: Optional[str] = Field(None, description="URL to book cover image")
    preview_url: Optional[str] = Field(None, description="URL to book preview")


class BookCreate(BookBase):
    """Schema for creating a book."""

    pass


class Book(BookBase):
    """Schema for book response."""

    id: int = Field(..., description="Unique book identifier")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "cover_image_url": "https://example.com/cover.jpg",
                "preview_url": "https://books.google.com/preview",
            }
        }


class BookSearchBase(BaseModel):
    """Base book search schema."""

    query: str = Field(..., description="Search query", min_length=1, max_length=256)
    search_count: int = Field(0, description="Number of times this query was searched")


class BookSearch(BookSearchBase):
    """Schema for book search response."""

    id: int = Field(..., description="Unique search identifier")
    books: List[Book] = Field(default_factory=list, description="List of books found")

    class Config:
        from_attributes = True


class BookRecommendationRequest(BaseModel):
    """Schema for book recommendation request."""

    query: str = Field(
        ...,
        description="What kind of book are you looking for?",
        min_length=3,
        max_length=500,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "I want a book about artificial intelligence and its impact on society"
            }
        }


class MovieRecommendationRequest(BaseModel):
    """Schema for movie recommendation request."""

    query: str = Field(
        ...,
        description="What kind of movie are you looking for?",
        min_length=3,
        max_length=500,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "I want a sci-fi movie with time travel and good special effects"
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    request_id: Optional[str] = Field(
        None, description="Request identifier for tracking"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Query must be at least 3 characters long",
                "request_id": "req_123456789",
            }
        }

"""Service layer for handling external API interactions."""

import logging
from typing import Dict, List, Optional, Any
import requests
from sqlalchemy.orm import Session

from app.config import settings
from app.exceptions import ExternalAPIError
from app.models import Book, BookSearch

logger = logging.getLogger(__name__)


class GoogleBooksService:
    """Service for interacting with Google Books API."""

    def __init__(self):
        self.api_key = settings.google_api_key
        self.base_url = "https://www.googleapis.com/books/v1/volumes"

    def get_book_details(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Fetch book details from Google Books API.

        Args:
            title: Book title to search for

        Returns:
            Dictionary containing book details or None if not found

        Raises:
            ExternalAPIError: When API call fails
        """
        try:
            query = f"intitle:{title}"
            params = {"q": query, "key": self.api_key}

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            books_data = response.json()

            if books_data.get("totalItems", 0) == 0:
                logger.warning(f"No books found for title: {title}")
                return None

            book_data = books_data["items"][0]
            volume_info = book_data.get("volumeInfo", {})

            # Extract book details with fallbacks
            author = volume_info.get("authors", ["Unknown Author"])[0]
            cover_image_url = (
                volume_info.get("imageLinks", {}).get("thumbnail")
                or "assets/images/image-err.png"
            )
            preview_link = volume_info.get("previewLink", "")

            return {
                "title": title,
                "author": author,
                "cover_image_url": cover_image_url,
                "preview_url": preview_link,
            }

        except requests.RequestException as e:
            logger.error(f"Google Books API error: {str(e)}")
            raise ExternalAPIError("Google Books", str(e))
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing Google Books response: {str(e)}")
            raise ExternalAPIError("Google Books", "Invalid response format")


class BookService:
    """Service for book-related business logic."""

    def __init__(self, google_books_service: GoogleBooksService):
        self.google_books_service = google_books_service

    def get_book_search_by_query(self, db: Session, query: str) -> Optional[BookSearch]:
        """Get book search record by query."""
        return db.query(BookSearch).filter(BookSearch.query == query).first()

    def get_book_by_title(self, db: Session, title: str) -> Optional[Book]:
        """Get book record by title."""
        return db.query(Book).filter(Book.title == title).first()

    def create_book_search(
        self, db: Session, query: str, book_titles: List[str]
    ) -> BookSearch:
        """
        Create a new book search record with associated books.

        Args:
            db: Database session
            query: Search query
            book_titles: List of book titles to associate

        Returns:
            Created BookSearch record
        """
        # Create or get book search record
        book_search = self.get_book_search_by_query(db, query)
        if not book_search:
            book_search = BookSearch(query=query, search_count=0)

        # Process each book title
        for title in book_titles:
            try:
                book_details = self.google_books_service.get_book_details(title)
                if not book_details:
                    continue

                # Check if book already exists
                db_book = self.get_book_by_title(db, book_details["title"])
                if not db_book:
                    db_book = Book(
                        title=book_details["title"],
                        author=book_details["author"],
                        preview_url=book_details["preview_url"],
                        cover_image_url=book_details["cover_image_url"],
                    )
                    db.add(db_book)

                # Add book to search results if not already present
                if db_book not in book_search.books:
                    book_search.books.append(db_book)

            except ExternalAPIError as e:
                logger.warning(f"Failed to get details for book '{title}': {str(e)}")
                continue

        # Update search count
        book_search.search_count += 1

        db.add(book_search)
        db.commit()
        db.refresh(book_search)

        return book_search

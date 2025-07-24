"""Book recommendation endpoints."""

import logging
from typing import List
from fastapi import Depends, APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas import Book as BookSchema
from app.dependency import get_db, get_openai_service, get_book_service
from app.services import OpenAIService, BookService
from app.exceptions import ExternalAPIError, InvalidQueryError, RateLimitExceededError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/books",
    tags=["books"],
    responses={404: {"description": "Not found"}},
)


@router.get("/suggest", summary="Get single book recommendation")
async def suggest_book(
    q: str = Query(..., description="Query for book recommendation", min_length=3),
    openai_service: OpenAIService = Depends(get_openai_service),
    book_service: BookService = Depends(get_book_service),
):
    """
    Get a single book recommendation based on user query.

    - **q**: The query describing what kind of book you're looking for

    Returns book details including title, author, cover image, preview URL, and description.
    """
    try:
        # Get book suggestion from OpenAI
        title, description = openai_service.suggest_single_book(q.strip())

        # Get book details from Google Books
        book_details = book_service.google_books_service.get_book_details(title)

        if not book_details:
            raise HTTPException(
                status_code=404,
                detail="Could not find book details for the suggested title",
            )

        # Add AI-generated description
        book_details["description"] = description

        logger.info(f"Successfully suggested book: {title}")
        return book_details

    except InvalidQueryError as e:
        logger.warning(f"Invalid query for book suggestion: {q}")
        raise HTTPException(status_code=400, detail=str(e))

    except RateLimitExceededError as e:
        logger.warning("Rate limit exceeded for book suggestion")
        raise HTTPException(status_code=429, detail=str(e))

    except ExternalAPIError as e:
        logger.error(f"External API error in book suggestion: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get(
    "/suggest-many",
    response_model=List[BookSchema],
    summary="Get multiple book recommendations",
)
async def suggest_books(
    q: str = Query(..., description="Query for book recommendations", min_length=3),
    db: Session = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service),
    book_service: BookService = Depends(get_book_service),
):
    """
    Get multiple book recommendations based on user query.

    - **q**: The query describing what kind of books you're looking for

    Returns a list of books with details including title, author, cover image, and preview URL.
    Results are cached to improve performance for repeated queries.
    """
    try:
        query = q.strip()

        # Check if we have cached results
        cached_search = book_service.get_book_search_by_query(db, query)
        if cached_search and cached_search.books:
            logger.info(f"Returning cached results for query: {query}")
            return cached_search.books

        # Get book suggestions from OpenAI
        book_titles = openai_service.suggest_multiple_books(query)

        if not book_titles:
            raise HTTPException(
                status_code=404,
                detail="No book recommendations could be generated for this query",
            )

        # Create book search record with details
        book_search = book_service.create_book_search(db, query, book_titles)

        if not book_search.books:
            raise HTTPException(
                status_code=404,
                detail="Could not find details for any of the suggested books",
            )

        logger.info(
            f"Successfully suggested {len(book_search.books)} books for query: {query}"
        )
        return book_search.books

    except InvalidQueryError as e:
        logger.warning(f"Invalid query for book suggestions: {q}")
        raise HTTPException(status_code=400, detail=str(e))

    except RateLimitExceededError as e:
        logger.warning("Rate limit exceeded for book suggestions")
        raise HTTPException(status_code=429, detail=str(e))

    except ExternalAPIError as e:
        logger.error(f"External API error in book suggestions: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

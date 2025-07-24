"""Movie recommendation endpoints."""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query

from app.dependency import get_openai_service, get_movie_service
from app.services import OpenAIService, MovieService
from app.exceptions import ExternalAPIError, InvalidQueryError, RateLimitExceededError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
    responses={404: {"description": "Not found"}},
)


@router.get("/suggest", summary="Get single movie recommendation")
async def suggest_movie(
    q: str = Query(..., description="Query for movie recommendation", min_length=3),
    openai_service: OpenAIService = Depends(get_openai_service),
    movie_service: MovieService = Depends(get_movie_service),
) -> Dict[str, Any]:
    """
    Get a single movie recommendation based on user query.

    - **q**: The query describing what kind of movie you're looking for

    Returns movie details including title, overview, poster, trailer, genres, and ratings.
    """
    try:
        # Get movie suggestion from OpenAI
        suggested_title = openai_service.suggest_single_movie(q.strip())

        # Get movie details from TMDB and YouTube
        movie_data = movie_service.get_movie_details(suggested_title)

        logger.info(f"Successfully suggested movie: {suggested_title}")
        return movie_data

    except InvalidQueryError as e:
        logger.warning(f"Invalid query for movie suggestion: {q}")
        raise HTTPException(status_code=400, detail=str(e))

    except RateLimitExceededError as e:
        logger.warning("Rate limit exceeded for movie suggestion")
        raise HTTPException(status_code=429, detail=str(e))

    except ExternalAPIError as e:
        logger.error(f"External API error in movie suggestion: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/suggest-many", summary="Get multiple movie recommendations")
async def suggest_movies(
    q: str = Query(..., description="Query for movie recommendations", min_length=3),
    openai_service: OpenAIService = Depends(get_openai_service),
    movie_service: MovieService = Depends(get_movie_service),
) -> List[Dict[str, Any]]:
    """
    Get multiple movie recommendations based on user query.

    - **q**: The query describing what kind of movies you're looking for

    Returns a list of movies with details including title, overview, poster, trailer, genres, and ratings.
    """
    try:
        query = q.strip()

        # Get movie suggestions from OpenAI
        movie_titles = openai_service.suggest_multiple_movies(query)

        if not movie_titles:
            raise HTTPException(
                status_code=404,
                detail="No movie recommendations could be generated for this query",
            )

        # Get details for each movie
        suggested_movies = []
        for idx, movie_title in enumerate(movie_titles, 1):
            try:
                movie_data = movie_service.get_movie_details(movie_title)
                movie_data["id"] = idx  # Add sequential ID for frontend
                suggested_movies.append(movie_data)

            except ExternalAPIError as e:
                logger.warning(
                    f"Failed to get details for movie '{movie_title}': {str(e)}"
                )
                continue

        if not suggested_movies:
            raise HTTPException(
                status_code=404,
                detail="Could not find details for any of the suggested movies",
            )

        logger.info(
            f"Successfully suggested {len(suggested_movies)} movies for query: {query}"
        )
        return suggested_movies

    except InvalidQueryError as e:
        logger.warning(f"Invalid query for movie suggestions: {q}")
        raise HTTPException(status_code=400, detail=str(e))

    except RateLimitExceededError as e:
        logger.warning("Rate limit exceeded for movie suggestions")
        raise HTTPException(status_code=429, detail=str(e))

    except ExternalAPIError as e:
        logger.error(f"External API error in movie suggestions: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

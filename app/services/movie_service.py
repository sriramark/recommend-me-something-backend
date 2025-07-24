"""Service layer for handling movie-related operations."""

import logging
from typing import Dict, Optional, Any
import requests

from app.config import settings
from app.exceptions import ExternalAPIError

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service for interacting with YouTube Data API."""

    def __init__(self):
        self.api_key = settings.youtube_data_api_key
        self.base_url = "https://www.googleapis.com/youtube/v3/search"

    def get_trailer_url(self, title: str) -> str:
        """
        Get YouTube trailer URL for a movie.

        Args:
            title: Movie title to search for

        Returns:
            YouTube URL or 'None' if not found
        """
        try:
            query = f"{title} movie trailer"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "key": self.api_key,
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            items = data.get("items", [])

            if items:
                video_id = items[0]["id"]["videoId"]
                return f"https://www.youtube.com/watch?v={video_id}"

            return "None"

        except (requests.RequestException, KeyError, IndexError) as e:
            logger.warning(f"Failed to get trailer for '{title}': {str(e)}")
            return "None"


class TMDBService:
    """Service for interacting with The Movie Database (TMDB) API."""

    def __init__(self):
        self.api_key = settings.tmdb_api_key
        self.base_url = "https://api.themoviedb.org/3"
        self._genre_cache: Optional[Dict[int, str]] = None

    def _get_genres(self) -> Dict[int, str]:
        """Get and cache movie genres from TMDB."""
        if self._genre_cache is None:
            try:
                url = f"{self.base_url}/genre/movie/list"
                params = {"api_key": self.api_key}

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()
                self._genre_cache = {
                    genre["id"]: genre["name"] for genre in data.get("genres", [])
                }

            except requests.RequestException as e:
                logger.error(f"Failed to fetch genres from TMDB: {str(e)}")
                self._genre_cache = {}

        return self._genre_cache

    def get_genre_name(self, genre_id: int) -> str:
        """Get genre name by ID."""
        genres = self._get_genres()
        return genres.get(genre_id, "Unknown Genre")

    def search_movie(self, title: str) -> Dict[str, Any]:
        """
        Search for a movie by title.

        Args:
            title: Movie title to search for

        Returns:
            Dictionary containing movie details

        Raises:
            ExternalAPIError: When API call fails or no results found
        """
        try:
            url = f"{self.base_url}/search/movie"
            params = {"api_key": self.api_key, "query": title}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            if not results:
                raise ExternalAPIError("TMDB", f"No movie found for title: {title}")

            movie_data = results[0]

            # Add additional fields
            poster_path = movie_data.get("poster_path")
            movie_data["poster_url"] = (
                f"https://image.tmdb.org/t/p/original/{poster_path}"
                if poster_path
                else None
            )

            # Convert genre IDs to names
            genre_ids = movie_data.get("genre_ids", [])
            movie_data["genre_names"] = [
                self.get_genre_name(genre_id) for genre_id in genre_ids
            ]

            return movie_data

        except requests.RequestException as e:
            logger.error(f"TMDB API error: {str(e)}")
            raise ExternalAPIError("TMDB", str(e))


class MovieService:
    """Service for movie-related business logic."""

    def __init__(self, tmdb_service: TMDBService, youtube_service: YouTubeService):
        self.tmdb_service = tmdb_service
        self.youtube_service = youtube_service

    def get_movie_details(self, title: str) -> Dict[str, Any]:
        """
        Get comprehensive movie details including trailer.

        Args:
            title: Movie title to search for

        Returns:
            Dictionary containing movie details with trailer URL

        Raises:
            ExternalAPIError: When movie details cannot be retrieved
        """
        try:
            # Get movie details from TMDB
            movie_data = self.tmdb_service.search_movie(title)

            # Add trailer URL from YouTube
            movie_data["trailer_url"] = self.youtube_service.get_trailer_url(title)

            return movie_data

        except ExternalAPIError:
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error getting movie details for '{title}': {str(e)}"
            )
            raise ExternalAPIError("MovieService", f"Failed to process movie: {title}")

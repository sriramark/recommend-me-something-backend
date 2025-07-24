"""Service layer for OpenAI API interactions."""

import logging
from typing import List
import openai
from openai.error import RateLimitError, OpenAIError

from app.config import settings
from app.exceptions import RateLimitExceededError, ExternalAPIError, InvalidQueryError

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""

    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens

    def _create_chat_completion(self, prompt: str) -> str:
        """
        Create a chat completion using OpenAI API.

        Args:
            prompt: The prompt to send to OpenAI

        Returns:
            The response content from OpenAI

        Raises:
            RateLimitExceededError: When rate limit is exceeded
            ExternalAPIError: When API call fails
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            return response["choices"][0]["message"]["content"].strip()

        except RateLimitError as e:
            logger.warning(f"OpenAI rate limit exceeded: {str(e)}")
            raise RateLimitExceededError(
                "OpenAI API rate limit exceeded. Please try again later."
            )

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise ExternalAPIError("OpenAI", str(e))

        except Exception as e:
            logger.error(f"Unexpected OpenAI error: {str(e)}")
            raise ExternalAPIError("OpenAI", "Unexpected error occurred")

    def suggest_single_book(self, query: str) -> tuple[str, str]:
        """
        Get a single book recommendation with description.

        Args:
            query: User query for book recommendation

        Returns:
            Tuple of (book_title, description)

        Raises:
            InvalidQueryError: When query cannot be processed
            RateLimitExceededError: When rate limit is exceeded
            ExternalAPIError: When API call fails
        """
        # Ensure query ends with a period
        if not query.endswith("."):
            query += "."

        prompt = (
            f"Recommend a book title and how it helps separated by '|' "
            f"without author name according to:\n{query}\n"
            f"Give output 'err' if query is not proper\n\nbook title:"
        )

        try:
            response = self._create_chat_completion(prompt)

            # Clean up response
            response = response.replace("'s", "s").replace('"', "")

            if response.lower() == "err":
                raise InvalidQueryError(
                    "Please provide a proper query for book recommendation"
                )

            # Split title and description
            parts = response.split("|")
            if len(parts) != 2:
                raise InvalidQueryError("Invalid response format from AI")

            title = parts[0].strip()
            description = parts[1].strip()

            return title, description

        except (RateLimitExceededError, ExternalAPIError):
            raise
        except Exception as e:
            logger.error(f"Error processing book suggestion: {str(e)}")
            raise InvalidQueryError("Failed to process book recommendation request")

    def suggest_multiple_books(self, query: str) -> List[str]:
        """
        Get multiple book recommendations.

        Args:
            query: User query for book recommendations

        Returns:
            List of book titles

        Raises:
            InvalidQueryError: When query cannot be processed
            RateLimitExceededError: When rate limit is exceeded
            ExternalAPIError: When API call fails
        """
        prompt = (
            f"{query} Suggest book titles without author name "
            f"in a single quoted python list according to my query."
        )

        try:
            response = self._create_chat_completion(prompt)

            # Clean up response
            response = response.replace("'s", "s")

            # Safely evaluate the response as a Python list
            try:
                book_titles = eval(response)
                if not isinstance(book_titles, list):
                    raise ValueError("Response is not a list")

                return [str(title) for title in book_titles]

            except (SyntaxError, ValueError):
                logger.warning(f"Failed to parse book list: {response}")
                raise InvalidQueryError(
                    "Please provide a proper query for book recommendations"
                )

        except (RateLimitExceededError, ExternalAPIError):
            raise
        except Exception as e:
            logger.error(f"Error processing multiple book suggestions: {str(e)}")
            raise InvalidQueryError("Failed to process book recommendations request")

    def suggest_single_movie(self, query: str) -> str:
        """
        Get a single movie recommendation.

        Args:
            query: User query for movie recommendation

        Returns:
            Movie title

        Raises:
            InvalidQueryError: When query cannot be processed
            RateLimitExceededError: When rate limit is exceeded
            ExternalAPIError: When API call fails
        """
        # Ensure query ends with a period
        if not query.endswith("."):
            query += "."

        prompt = (
            f"Recommend a single movie title according to:\n{query}\n"
            f"Give output 'err' if query is not proper\n\nMovie title:"
        )

        try:
            response = self._create_chat_completion(prompt)

            # Clean up response
            response = response.replace('"', "").strip()

            if response.lower() in ["err", "error"]:
                raise InvalidQueryError(
                    "Please provide a proper query for movie recommendation"
                )

            return response

        except (RateLimitExceededError, ExternalAPIError):
            raise
        except Exception as e:
            logger.error(f"Error processing movie suggestion: {str(e)}")
            raise InvalidQueryError("Failed to process movie recommendation request")

    def suggest_multiple_movies(self, query: str) -> List[str]:
        """
        Get multiple movie recommendations.

        Args:
            query: User query for movie recommendations

        Returns:
            List of movie titles

        Raises:
            InvalidQueryError: When query cannot be processed
            RateLimitExceededError: When rate limit is exceeded
            ExternalAPIError: When API call fails
        """
        # Ensure query ends with a period
        if not query.endswith("."):
            query += "."

        prompt = (
            f"Recommend movie titles in a double quoted python list according to:\n{query}\n\n"
            f"Movie titles in python list:"
        )

        try:
            response = self._create_chat_completion(prompt)

            # Safely evaluate the response as a Python list
            try:
                movie_titles = eval(response)
                if not isinstance(movie_titles, list):
                    raise ValueError("Response is not a list")

                return [str(title) for title in movie_titles]

            except (SyntaxError, ValueError):
                logger.warning(f"Failed to parse movie list: {response}")
                raise InvalidQueryError(
                    "Please provide a proper query for movie recommendations"
                )

        except (RateLimitExceededError, ExternalAPIError):
            raise
        except Exception as e:
            logger.error(f"Error processing multiple movie suggestions: {str(e)}")
            raise InvalidQueryError("Failed to process movie recommendations request")

"""Test script for the Recommend Me Something API."""

import sys
import asyncio
import logging
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.config import settings
    from app.logging_config import setup_logging
    from app.services import OpenAIService, GoogleBooksService
    from app.services import TMDBService, YouTubeService, MovieService
except ImportError as e:
    print(f"Import error: {e}")
    print(
        "Make sure you have all dependencies installed: pip install -r requirements.txt"
    )
    sys.exit(1)


async def test_configuration():
    """Test application configuration."""
    print("=" * 50)
    print("TESTING CONFIGURATION")
    print("=" * 50)

    print(f"App Name: {settings.app_name}")
    print(f"App Version: {settings.app_version}")
    print(f"Debug Mode: {settings.debug}")

    # Check if required environment variables are set
    required_keys = [
        "database_url",
        "openai_api_key",
        "google_api_key",
        "tmdb_api_key",
        "youtube_data_api_key",
    ]

    for key in required_keys:
        value = getattr(settings, key, None)
        status = "✓" if value else "✗"
        print(f"{status} {key.upper()}: {'Set' if value else 'Missing'}")

    print()


async def test_openai_service():
    """Test OpenAI service functionality."""
    print("=" * 50)
    print("TESTING OPENAI SERVICE")
    print("=" * 50)

    try:
        openai_service = OpenAIService()

        # Test single book suggestion
        print("Testing single book suggestion...")
        try:
            title, description = openai_service.suggest_single_book("science fiction")
            print(f"✓ Book suggestion: {title}")
            print(f"  Description: {description[:100]}...")
        except Exception as e:
            print(f"✗ Book suggestion failed: {str(e)}")

        # Test single movie suggestion
        print("\nTesting single movie suggestion...")
        try:
            movie_title = openai_service.suggest_single_movie("action movie")
            print(f"✓ Movie suggestion: {movie_title}")
        except Exception as e:
            print(f"✗ Movie suggestion failed: {str(e)}")

    except Exception as e:
        print(f"✗ OpenAI service initialization failed: {str(e)}")

    print()


async def test_google_books_service():
    """Test Google Books service functionality."""
    print("=" * 50)
    print("TESTING GOOGLE BOOKS SERVICE")
    print("=" * 50)

    try:
        google_service = GoogleBooksService()

        print("Testing book details retrieval...")
        book_details = google_service.get_book_details("The Great Gatsby")

        if book_details:
            print("✓ Book details retrieved successfully:")
            print(f"  Title: {book_details['title']}")
            print(f"  Author: {book_details['author']}")
            print(f"  Cover URL: {book_details['cover_image_url'][:50]}...")
        else:
            print("✗ No book details found")

    except Exception as e:
        print(f"✗ Google Books service failed: {str(e)}")

    print()


async def test_tmdb_service():
    """Test TMDB service functionality."""
    print("=" * 50)
    print("TESTING TMDB SERVICE")
    print("=" * 50)

    try:
        tmdb_service = TMDBService()

        print("Testing movie search...")
        movie_data = tmdb_service.search_movie("The Matrix")

        if movie_data:
            print("✓ Movie details retrieved successfully:")
            print(f"  Title: {movie_data['title']}")
            print(f"  Overview: {movie_data['overview'][:100]}...")
            print(f"  Release Date: {movie_data['release_date']}")
            print(f"  Genres: {', '.join(movie_data['genre_names'])}")
        else:
            print("✗ No movie details found")

    except Exception as e:
        print(f"✗ TMDB service failed: {str(e)}")

    print()


async def test_youtube_service():
    """Test YouTube service functionality."""
    print("=" * 50)
    print("TESTING YOUTUBE SERVICE")
    print("=" * 50)

    try:
        youtube_service = YouTubeService()

        print("Testing trailer URL retrieval...")
        trailer_url = youtube_service.get_trailer_url("The Matrix")

        if trailer_url and trailer_url != "None":
            print(f"✓ Trailer URL retrieved: {trailer_url}")
        else:
            print("✗ No trailer URL found")

    except Exception as e:
        print(f"✗ YouTube service failed: {str(e)}")

    print()


async def test_integrated_services():
    """Test integrated service functionality."""
    print("=" * 50)
    print("TESTING INTEGRATED SERVICES")
    print("=" * 50)

    try:
        # Test movie service integration
        tmdb_service = TMDBService()
        youtube_service = YouTubeService()
        movie_service = MovieService(tmdb_service, youtube_service)

        print("Testing integrated movie service...")
        movie_details = movie_service.get_movie_details("Inception")

        if movie_details:
            print("✓ Integrated movie service working:")
            print(f"  Title: {movie_details['title']}")
            print(
                f"  Has trailer: {'Yes' if movie_details.get('trailer_url') != 'None' else 'No'}"
            )
            print(f"  Has poster: {'Yes' if movie_details.get('poster_url') else 'No'}")

    except Exception as e:
        print(f"✗ Integrated services failed: {str(e)}")

    print()


def test_logging():
    """Test logging configuration."""
    print("=" * 50)
    print("TESTING LOGGING")
    print("=" * 50)

    try:
        setup_logging("INFO")
        logger = logging.getLogger("test_logger")

        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")

        print("✓ Logging configuration successful")
        print("✓ Check logs/app.log for log output")

    except Exception as e:
        print(f"✗ Logging configuration failed: {str(e)}")

    print()


async def main():
    """Run all tests."""
    print("RECOMMEND ME SOMETHING API - TEST SUITE")
    print("=" * 50)
    print()

    # Test configuration
    await test_configuration()

    # Test logging
    test_logging()

    # Only run API tests if we have the required environment variables
    if settings.openai_api_key:
        await test_openai_service()
    else:
        print("Skipping OpenAI tests - API key not configured")
        print()

    if settings.google_api_key:
        await test_google_books_service()
    else:
        print("Skipping Google Books tests - API key not configured")
        print()

    if settings.tmdb_api_key:
        await test_tmdb_service()
    else:
        print("Skipping TMDB tests - API key not configured")
        print()

    if settings.youtube_data_api_key:
        await test_youtube_service()
    else:
        print("Skipping YouTube tests - API key not configured")
        print()

    # Test integrated services if we have all keys
    if all([settings.tmdb_api_key, settings.youtube_data_api_key]):
        await test_integrated_services()
    else:
        print("Skipping integrated service tests - API keys not configured")
        print()

    print("=" * 50)
    print("TEST SUITE COMPLETED")
    print("=" * 50)
    print()
    print("Note: Some tests may be skipped if API keys are not configured.")
    print(
        "To run all tests, ensure all required environment variables are set in .env file."
    )


if __name__ == "__main__":
    asyncio.run(main())

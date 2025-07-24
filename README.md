# Recommend Me Something API

A modern, AI-powered recommendation API that provides personalized book and movie suggestions based on user queries. Built with FastAPI, powered by OpenAI, and integrated with Google Books and The Movie Database (TMDB).

## 🚀 Features

- **AI-Powered Recommendations**: Uses OpenAI's GPT-3.5 to understand user preferences and provide intelligent suggestions
- **Book Recommendations**: Get personalized book suggestions with details from Google Books API
- **Movie Recommendations**: Discover movies with comprehensive details from TMDB and YouTube trailers
- **Caching**: Smart caching system for book searches to improve performance
- **Professional Architecture**: Clean separation of concerns with services, dependency injection, and error handling
- **Comprehensive Logging**: Structured logging for monitoring and debugging
- **API Documentation**: Interactive Swagger/OpenAPI documentation
- **Health Checks**: Built-in health monitoring endpoints

## 🛠 Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI/ML**: OpenAI GPT-3.5 Turbo
- **External APIs**:
  - Google Books API
  - The Movie Database (TMDB)
  - YouTube Data API
- **Configuration**: Pydantic Settings with environment variables
- **Logging**: Python's built-in logging with custom configuration

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- API keys for:
  - OpenAI
  - Google Books API
  - The Movie Database (TMDB)
  - YouTube Data API

## ⚙️ Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd API
   ```

2. **Create virtual environment**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:

   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/database_name
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_books_api_key
   TMDB_API_KEY=your_tmdb_api_key
   YOUTUBE_DATA_API_KEY=your_youtube_api_key
   DEBUG=false
   ```

5. **Database Setup**
   ```bash
   # The application will automatically create tables on startup
   # Ensure your PostgreSQL database is running and accessible
   ```

## 🚀 Running the Application

### Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Using Heroku

The application includes a `Procfile` for Heroku deployment:

```bash
git push heroku main
```

## 📖 API Documentation

Once the application is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔗 API Endpoints

### Root & Health

- `GET /` - API information and available endpoints
- `GET /health` - Health check endpoint

### Books

- `GET /books/suggest?q={query}` - Get single book recommendation
- `GET /books/suggest-many?q={query}` - Get multiple book recommendations

### Movies

- `GET /movies/suggest?q={query}` - Get single movie recommendation
- `GET /movies/suggest-many?q={query}` - Get multiple movie recommendations

### Example Requests

**Single Book Recommendation:**

```bash
curl "http://localhost:8000/books/suggest?q=I want a book about artificial intelligence"
```

**Multiple Movie Recommendations:**

```bash
curl "http://localhost:8000/movies/suggest-many?q=sci-fi movies with time travel"
```

## 📁 Project Structure

```
app/
├── __init__.py
├── main.py                 # FastAPI application and middleware setup
├── config.py              # Application configuration management
├── database.py            # Database connection and setup
├── dependency.py          # Dependency injection
├── exceptions.py          # Custom exceptions and error handlers
├── logging_config.py      # Logging configuration
├── models.py              # SQLAlchemy database models
├── schemas.py             # Pydantic request/response models
├── routers/               # API route handlers
│   ├── __init__.py
│   ├── books.py           # Book recommendation endpoints
│   └── movies.py          # Movie recommendation endpoints
└── services/              # Business logic layer
    ├── __init__.py
    ├── book_service.py     # Book-related business logic
    ├── movie_service.py    # Movie-related business logic
    └── openai_service.py   # OpenAI API interactions
```

## 🔧 Configuration

The application uses environment variables for configuration. Key settings include:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for AI recommendations
- `GOOGLE_API_KEY`: Google Books API key
- `TMDB_API_KEY`: The Movie Database API key
- `YOUTUBE_DATA_API_KEY`: YouTube Data API key for trailers
- `DEBUG`: Enable/disable debug mode

Additional configuration can be found in `config.py` and `config.yml`.

## 📊 Logging

The application includes comprehensive logging:

- Console output for development
- File logging to `logs/app.log`
- Structured log levels for different components
- Request tracking with unique request IDs

## 🛡️ Error Handling

Professional error handling with:

- Custom exception classes for different error types
- Consistent error response format
- Proper HTTP status codes
- Detailed error logging for debugging

## 🔄 Caching

- Book search results are cached in the database
- Repeated queries return cached results for improved performance
- Search count tracking for analytics

## 🧪 Testing

Run the test file:

```bash
python test.py
```

## 📈 Performance Considerations

- Database connection pooling
- Efficient caching strategy
- Proper error handling to prevent cascading failures
- Rate limiting awareness for external APIs
- Async/await pattern for better concurrency

## 🚀 Deployment

### Heroku

1. Create a Heroku app
2. Add environment variables in Heroku Config Vars
3. Deploy using Git:
   ```bash
   git push heroku main
   ```

### Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs in `logs/app.log`

## 🔮 Future Enhancements

- User authentication and personalized recommendations
- Machine learning-based recommendation improvements
- Support for additional content types (music, podcasts, etc.)
- Real-time recommendations
- Advanced filtering and sorting options
- Recommendation explanations and similarity scores

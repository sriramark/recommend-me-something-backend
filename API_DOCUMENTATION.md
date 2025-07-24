# API Documentation

## Overview

The Recommend Me Something API provides AI-powered recommendations for books and movies based on user queries. It leverages OpenAI's GPT-3.5 model to understand user preferences and returns detailed information about recommended content.

## Base URL

```
https://your-api-domain.com
```

## Authentication

Currently, this API does not require authentication. However, it does require valid API keys for external services to be configured on the server side.

## Rate Limiting

- **Rate Limit**: 60 requests per minute per IP address
- **OpenAI Rate Limits**: Subject to OpenAI's rate limiting policies

When rate limits are exceeded, you'll receive a `429 Too Many Requests` response.

## Error Handling

All error responses follow a consistent format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error description",
  "request_id": "unique_request_identifier"
}
```

### Common HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid query parameters)
- `404` - Not Found (no recommendations found)
- `429` - Too Many Requests (rate limit exceeded)
- `503` - Service Unavailable (external API error)
- `500` - Internal Server Error

## Endpoints

### Books

#### Get Single Book Recommendation

**GET** `/books/suggest`

Get a single book recommendation with description based on user query.

**Query Parameters:**

- `q` (required): The query describing what kind of book you're looking for (minimum 3 characters)

**Example Request:**

```bash
GET /books/suggest?q=I want a book about artificial intelligence and its impact on society
```

**Example Response:**

```json
{
  "title": "Weapons of Math Destruction",
  "author": "Cathy O'Neil",
  "cover_image_url": "https://books.google.com/books/content?id=...",
  "preview_url": "https://books.google.com/books?id=...",
  "description": "This book explores how algorithms and big data can perpetuate inequality and bias in society."
}
```

#### Get Multiple Book Recommendations

**GET** `/books/suggest-many`

Get multiple book recommendations based on user query. Results are cached for better performance.

**Query Parameters:**

- `q` (required): The query describing what kind of books you're looking for (minimum 3 characters)

**Example Request:**

```bash
GET /books/suggest-many?q=science fiction books about space exploration
```

**Example Response:**

```json
[
  {
    "id": 1,
    "title": "The Martian",
    "author": "Andy Weir",
    "cover_image_url": "https://books.google.com/books/content?id=...",
    "preview_url": "https://books.google.com/books?id=..."
  },
  {
    "id": 2,
    "title": "Packing for Mars",
    "author": "Mary Roach",
    "cover_image_url": "https://books.google.com/books/content?id=...",
    "preview_url": "https://books.google.com/books?id=..."
  }
]
```

### Movies

#### Get Single Movie Recommendation

**GET** `/movies/suggest`

Get a single movie recommendation based on user query.

**Query Parameters:**

- `q` (required): The query describing what kind of movie you're looking for (minimum 3 characters)

**Example Request:**

```bash
GET /movies/suggest?q=I want a sci-fi movie with time travel
```

**Example Response:**

```json
{
  "id": 550,
  "title": "Back to the Future",
  "overview": "Eighties teenager Marty McFly is accidentally sent back in time to 1955...",
  "poster_path": "/fNOH9f1aA7XRTzl1sAOx9iF553Q.jpg",
  "poster_url": "https://image.tmdb.org/t/p/original/fNOH9f1aA7XRTzl1sAOx9iF553Q.jpg",
  "release_date": "1985-07-03",
  "vote_average": 8.5,
  "vote_count": 15234,
  "genre_ids": [12, 35, 878],
  "genre_names": ["Adventure", "Comedy", "Science Fiction"],
  "trailer_url": "https://www.youtube.com/watch?v=qvsgGtivCgs"
}
```

#### Get Multiple Movie Recommendations

**GET** `/movies/suggest-many`

Get multiple movie recommendations based on user query.

**Query Parameters:**

- `q` (required): The query describing what kind of movies you're looking for (minimum 3 characters)

**Example Request:**

```bash
GET /movies/suggest-many?q=action movies with superheroes
```

**Example Response:**

```json
[
  {
    "id": 1,
    "title": "The Avengers",
    "overview": "When an unexpected enemy emerges and threatens global safety...",
    "poster_url": "https://image.tmdb.org/t/p/original/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg",
    "release_date": "2012-04-25",
    "vote_average": 7.7,
    "genre_names": ["Action", "Adventure", "Science Fiction"],
    "trailer_url": "https://www.youtube.com/watch?v=eOrNdBpGMv8"
  },
  {
    "id": 2,
    "title": "Iron Man",
    "overview": "After being held captive in an Afghan cave...",
    "poster_url": "https://image.tmdb.org/t/p/original/78lPtwv72eTNqFW9COBYI0dWDJa.jpg",
    "release_date": "2008-04-30",
    "vote_average": 7.6,
    "genre_names": ["Action", "Science Fiction", "Adventure"],
    "trailer_url": "https://www.youtube.com/watch?v=8ugaeA-nMTc"
  }
]
```

### System

#### Root Endpoint

**GET** `/`

Get API information and available endpoints.

**Example Response:**

```json
{
  "name": "Recommend Me Something API",
  "version": "1.0.0",
  "description": "API for Recommend Me Something - Get personalized book and movie recommendations",
  "docs_url": "/docs",
  "endpoints": {
    "books": "/books",
    "movies": "/movies"
  }
}
```

#### Health Check

**GET** `/health`

Check API health status.

**Example Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Data Models

### Book

```json
{
  "id": "integer",
  "title": "string",
  "author": "string | null",
  "cover_image_url": "string | null",
  "preview_url": "string | null"
}
```

### Movie

```json
{
  "id": "integer",
  "title": "string",
  "overview": "string",
  "poster_path": "string",
  "poster_url": "string",
  "release_date": "string (YYYY-MM-DD)",
  "vote_average": "number",
  "vote_count": "integer",
  "genre_ids": "array of integers",
  "genre_names": "array of strings",
  "trailer_url": "string"
}
```

## Usage Examples

### Python with requests

```python
import requests

# Get book recommendation
response = requests.get(
    "https://your-api-domain.com/books/suggest",
    params={"q": "mystery novels set in Victorian England"}
)
book = response.json()
print(f"Recommended book: {book['title']} by {book['author']}")

# Get movie recommendations
response = requests.get(
    "https://your-api-domain.com/movies/suggest-many",
    params={"q": "romantic comedies from the 90s"}
)
movies = response.json()
for movie in movies:
    print(f"- {movie['title']} ({movie['release_date'][:4]})")
```

### JavaScript with fetch

```javascript
// Get book recommendation
async function getBookRecommendation(query) {
  const response = await fetch(
    `https://your-api-domain.com/books/suggest?q=${encodeURIComponent(query)}`
  );
  const book = await response.json();
  return book;
}

// Get movie recommendations
async function getMovieRecommendations(query) {
  const response = await fetch(
    `https://your-api-domain.com/movies/suggest-many?q=${encodeURIComponent(
      query
    )}`
  );
  const movies = await response.json();
  return movies;
}

// Usage
getBookRecommendation("books about machine learning").then((book) =>
  console.log("Recommended book:", book.title)
);

getMovieRecommendations("thriller movies").then((movies) =>
  movies.forEach((movie) => console.log(movie.title))
);
```

### cURL

```bash
# Get single book recommendation
curl -X GET "https://your-api-domain.com/books/suggest?q=fantasy%20books%20with%20dragons" \
     -H "accept: application/json"

# Get multiple movie recommendations
curl -X GET "https://your-api-domain.com/movies/suggest-many?q=sci-fi%20movies%20about%20AI" \
     -H "accept: application/json"

# Health check
curl -X GET "https://your-api-domain.com/health" \
     -H "accept: application/json"
```

## Best Practices

1. **Query Optimization**: Be specific in your queries for better recommendations
2. **Error Handling**: Always handle potential error responses in your client code
3. **Rate Limiting**: Implement client-side rate limiting to avoid hitting API limits
4. **Caching**: Consider caching responses on the client side for repeated queries
5. **Timeouts**: Set appropriate timeout values for API requests

## Support

For technical support or questions about the API:

- Check the interactive documentation at `/docs`
- Review error messages and status codes
- Contact the development team

## Changelog

### Version 1.0.0

- Initial release
- Book and movie recommendation endpoints
- AI-powered suggestions using OpenAI GPT-3.5
- Integration with Google Books, TMDB, and YouTube APIs
- Comprehensive error handling and logging

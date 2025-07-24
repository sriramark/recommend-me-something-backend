# Deployment Guide

This guide covers various deployment options for the Recommend Me Something API.

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Local Deployment](#local-deployment)
3. [Heroku Deployment](#heroku-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Production Considerations](#production-considerations)
6. [Environment Variables](#environment-variables)
7. [Database Setup](#database-setup)
8. [Monitoring](#monitoring)

## Environment Setup

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Required API keys:
  - OpenAI API key
  - Google Books API key
  - TMDB API key
  - YouTube Data API key

### API Key Setup

1. **OpenAI API Key**

   - Sign up at [OpenAI](https://platform.openai.com/)
   - Create an API key in your dashboard
   - Set billing and usage limits

2. **Google Books API Key**

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Google Books API
   - Create credentials (API key)

3. **TMDB API Key**

   - Register at [The Movie Database](https://www.themoviedb.org/)
   - Request an API key from your account settings

4. **YouTube Data API Key**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the YouTube Data API v3
   - Create credentials (API key)

## Local Deployment

### 1. Clone and Setup

```bash
git clone <repository-url>
cd API

# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/recommend_me_something
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_books_api_key
TMDB_API_KEY=your_tmdb_api_key
YOUTUBE_DATA_API_KEY=your_youtube_data_api_key
DEBUG=true
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb recommend_me_something

# The application will automatically create tables on startup
```

### 4. Run the Application

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Heroku Deployment

### 1. Prerequisites

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login
```

### 2. Create Heroku App

```bash
# Create app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini
```

### 3. Set Environment Variables

```bash
heroku config:set OPENAI_API_KEY=your_openai_api_key
heroku config:set GOOGLE_API_KEY=your_google_books_api_key
heroku config:set TMDB_API_KEY=your_tmdb_api_key
heroku config:set YOUTUBE_DATA_API_KEY=your_youtube_data_api_key
heroku config:set DEBUG=false
```

### 4. Deploy

```bash
# Deploy to Heroku
git push heroku main

# Check logs
heroku logs --tail
```

### 5. Scale (Optional)

```bash
# Scale to multiple dynos
heroku ps:scale web=2
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Create docker-compose.yml

```yaml
version: "3.8"

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/recommend_me_something
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - TMDB_API_KEY=${TMDB_API_KEY}
      - YOUTUBE_DATA_API_KEY=${YOUTUBE_DATA_API_KEY}
      - DEBUG=false
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=recommend_me_something
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### 3. Deploy with Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f web
```

## Production Considerations

### 1. Security

- Use HTTPS in production
- Set `DEBUG=false`
- Use strong database passwords
- Restrict CORS origins
- Use environment variables for secrets
- Enable rate limiting

### 2. Performance

- Use multiple workers: `--workers 4`
- Configure database connection pooling
- Implement caching (Redis)
- Use a reverse proxy (nginx)
- Enable compression

### 3. Monitoring

- Set up application monitoring
- Configure error tracking (Sentry)
- Monitor API usage and rate limits
- Set up health checks

### 4. Scaling

- Use load balancers
- Implement horizontal scaling
- Monitor resource usage
- Consider using managed services

## Environment Variables

### Required Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# API Keys
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
TMDB_API_KEY=...
YOUTUBE_DATA_API_KEY=AIza...
```

### Optional Variables

```env
# Application
DEBUG=false
APP_NAME="Recommend Me Something API"
APP_VERSION="1.0.0"

# CORS
CORS_ORIGINS=["https://yourdomain.com"]
CORS_METHODS=["GET", "POST"]
CORS_ALLOW_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# OpenAI Configuration
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
```

## Database Setup

### PostgreSQL Setup

```sql
-- Create database
CREATE DATABASE recommend_me_something;

-- Create user (optional)
CREATE USER api_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE recommend_me_something TO api_user;
```

### Database Migrations

The application automatically creates tables on startup using SQLAlchemy. For production, consider using Alembic for migrations:

```bash
# Install Alembic
pip install alembic

# Initialize migrations
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## Monitoring

### Health Checks

The application provides health check endpoints:

- `GET /health` - Basic health check
- `GET /` - API information

### Logging

Logs are written to:

- Console (stdout)
- File: `logs/app.log`

### Application Monitoring

Consider using:

- **Sentry** for error tracking
- **New Relic** for APM
- **Datadog** for infrastructure monitoring
- **Prometheus + Grafana** for metrics

### Database Monitoring

Monitor:

- Connection pool usage
- Query performance
- Database size
- Active connections

## Troubleshooting

### Common Issues

1. **Import Errors**

   ```bash
   pip install -r requirements.txt
   ```

2. **Database Connection Issues**

   - Check DATABASE_URL format
   - Verify database is running
   - Check network connectivity

3. **API Key Issues**

   - Verify all required keys are set
   - Check API key permissions
   - Monitor API usage limits

4. **Performance Issues**
   - Check database queries
   - Monitor external API response times
   - Verify resource limits

### Debugging

```bash
# Enable debug mode
export DEBUG=true

# Check logs
tail -f logs/app.log

# Test configuration
python test_new.py
```

## SSL/HTTPS Setup

### Using nginx (Recommended)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Using Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

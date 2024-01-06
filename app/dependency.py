import os
from pathlib import Path
from dotenv import load_dotenv
from .database import SessionLocal, engine
from . import  models

# Enviroinmental variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
YOUTUBE_DATA_API_KEY = os.getenv("YOUTUBE_DATA_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

models.Base.metadata.create_all(bind=engine)

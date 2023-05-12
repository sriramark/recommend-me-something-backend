import os
from dotenv import load_dotenv
from pathlib import Path
import openai
from openai.error import RateLimitError
import requests

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
    responses={404: {"description": "Not found"}},
)


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(os.path.join(BASE_DIR, ".env"))

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
YOUTUBE_DATA_API_KEY = os.getenv("YOUTUBE_DATA_API_KEY")

openai.api_key = OPENAI_API_KEY


def get_trailer_url(title):
    query = title + 'movie trailer'

    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'key': YOUTUBE_DATA_API_KEY
    }

    response = requests.get('https://www.googleapis.com/youtube/v3/search', params=params)
    video_id = response.json()['items'][0]['id']['videoId']

    trailer_url = f'https://www.youtube.com/watch?v={video_id}'

    return trailer_url

def get_movie_detail(title):
    url = "https://api.themoviedb.org/3/search/movie"

    api_key = TMDB_API_KEY

    params = {
        "api_key": api_key,
        "query":title
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        data = data["results"][0]

        data['trailer_url'] = get_trailer_url(title)
        data['poster_url'] = f'https://image.tmdb.org/t/p/original/{data["poster_path"]}'

        return data
    
    return {"status":"failed"}


@router.get("/suggest")
async def suggest_movie(q : str):
    if q[-1] != '.':
        q += '.'
    prompt = "Recommend a movie title according to:\n" + q + "\n Give output 'err' if query is not proper" + '\n\n Movie title:'
    
    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature = 0.7,
        messages=[   
            {"role": "user", "content": prompt} 
            ]
        )

    except RateLimitError:
        raise HTTPException(status_code=429, detail='Request limit rate reached')
    
    suggested_movie = response['choices'][0]['message']['content']
    suggested_movie = suggested_movie.replace('"', '')

    if suggested_movie == 'err':
        raise HTTPException(status_code=404, detail='Provide proper query')
    
    movie_data = get_movie_detail(suggested_movie)
    return movie_data


@router.get("/suggest-many")
async def suggest_movies(q : str):
    if q[-1] != '.':
        q += '.'

    prompt = "Recommend movie titles in python list according to:\n" + q + '\n\n Movie titles in python list:'    

    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature = 0.7,
        messages=[
                {"role": "user", "content": prompt},
            ]
        )
    except RateLimitError:
        raise HTTPException(status_code=429, detail='Request limit rate reached')
    
    movies = response['choices'][0]['message']['content']
    print(movies)
    try:
        print(movies)
        suggested_movies_title =  eval(movies)
    except:
        raise HTTPException(status_code=500, detail='Provide proper query')  

    suggested_movies = []
    movie_sno = 1
    for movie_title in suggested_movies_title:
            movie = get_movie_detail(movie_title)
            movie['id'] = movie_sno
            suggested_movies.append(movie)

            movie_sno += 1
    
    return suggested_movies     
    

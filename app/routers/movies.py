import openai
from openai.error import RateLimitError
import requests

from fastapi import APIRouter, HTTPException
from app.dependency import OPENAI_API_KEY, TMDB_API_KEY, YOUTUBE_DATA_API_KEY

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
    responses={404: {"description": "Not found"}},
)

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
    try:
        video_id = response.json()['items'][0]['id']['videoId']
        trailer_url = f'https://www.youtube.com/watch?v={video_id}'
    except:
        trailer_url = 'None'

    return trailer_url

def get_genre_name(genre_id):
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}'

    response = requests.get(url)
    data = response.json()

    genres = data['genres']
    for genre in genres:
        if genre['id'] == genre_id:
            return genre['name']

    return 'Genre not found'

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
        try:
            data = data["results"][0]
        except:
            raise HTTPException(status_code=500, detail='Could not process the request')

        data['trailer_url'] = get_trailer_url(title)
        data['poster_url'] = f'https://image.tmdb.org/t/p/original/{data["poster_path"]}'

        genre_names = []
        for genre_id in data['genre_ids']:
            genre_names.append(get_genre_name(genre_id))

        data['genre_names'] = genre_names
        return data
    
    return {"status":"failed"}


@router.get("/suggest")
async def suggest_movie(q : str):
    if q[-1] != '.':
        q += '.'
    prompt = "Recommend a single movie title according to:\n" + q + "\n Give output 'err' if query is not proper" + '\n\n Movie title:'
    
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

    if suggested_movie == 'err' or suggested_movie == 'Err':
        raise HTTPException(status_code=404, detail='Provide proper query')
    
    movie_data = get_movie_detail(suggested_movie)
    return movie_data


@router.get("/suggest-many")
async def suggest_movies(q : str):
    if q[-1] != '.':
        q += '.'

    prompt = "Recommend movie titles in a double quoted python list according to:\n" + q + '\n\n Movie titles in python list:'    

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
    try:
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
    

import os
from dotenv import load_dotenv
import openai
import requests
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/books",
    tags=["books"],
    responses={404: {"description": "Not found"}},
)

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, ".env"))

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

openai.api_key = OPENAI_API_KEY

def get_book_detail(title):  
    query = f"intitle:{title}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    books_data = response.json() # Multiple books will be returned

    if books_data['totalItems'] != 0:
        book = books_data['items'][0] # First book 
        try:
            author = book['volumeInfo']['authors'][0] 
        except KeyError:
            author = 'Author not found'
        
        try:
            cover_image_url = book['volumeInfo']['imageLinks']['thumbnail']
        except KeyError:
            cover_image_url = 'assets/images/image-err.png'
        
        preview_link = book['volumeInfo']['previewLink']

        book_detail = {
            'title':title,
            'author':author,
            'cover_image_url':cover_image_url, 
            'preview_url' : preview_link
        }

        return book_detail

@router.get("/suggest-many")
async def suggest_books(q : str):
    prompt = q + " Suggest book titles without author name in a single quoted python list according to my query."

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    temperature = 0.7,
    messages=[
            {"role": "user", "content": prompt},
        ]
    )

    books = response['choices'][0]['message']['content']
    books = books.replace("'s", 's')
    print(books)
    try:
        suggested_books_title =  eval(books)
    except:
        raise HTTPException(status_code=404, detail=books)
    
    suggested_books = []
    book_sno = 1
    for book_title in suggested_books_title:
            book = get_book_detail(book_title)
            book['id'] = book_sno
            suggested_books.append(book)

            book_sno += 1
    
    return suggested_books


@router.get("/suggest")
async def suggest_book(q : str):
    if q[-1] != '.':
        q += '.'

    prompt = q + " Suggest a book according to my query in JSON format containing data of book's title and how it helps in variables title and helps."
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    temperature = 0.7,
    messages=[
            {"role": "user", "content": prompt},
        ]
    )

    suggested_book = response['choices'][0]['message']['content']
    suggested_book = suggested_book.replace("'s", 's')
    try:
        suggested_book = eval(suggested_book)
    except:
        raise HTTPException(status_code=404, detail={'detail':'Please provide proper query'})
    
    title = suggested_book['title']
    book_data = get_book_detail(title)
    book_data['description'] = suggested_book['helps']
    
    return book_data

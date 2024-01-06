from fastapi import Depends, APIRouter, HTTPException
import openai
from openai.error import RateLimitError
import requests
from sqlalchemy.orm import Session

from app.models import Book, BookSearch
from app.dependency import OPENAI_API_KEY, GOOGLE_API_KEY, get_db

router = APIRouter(
    prefix="/books",
    tags=["books"],
    responses={404: {"description": "Not found"}},
)

openai.api_key = OPENAI_API_KEY

def get_book_search_by_query(db: Session, q:str):
    return db.query(BookSearch).filter(BookSearch.query==q).first()

def get_book_by_title(db: Session, title:str):
    return db.query(Book).filter(Book.title==title).first()

def get_book_detail(title):
    """
    Fetches books info from google books API
    """
    query = f"intitle:{title}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    books_data = response.json() # Multiple books will be returned

    if books_data['totalItems'] != 0:
        book_data = books_data['items'][0] # First book 

        try:
            author = book_data['volumeInfo']['authors'][0] 
        except KeyError:
            author = 'Author not found'
        
        try:
            cover_image_url = book_data['volumeInfo']['imageLinks']['thumbnail']
        except KeyError:
            cover_image_url = 'assets/images/image-err.png'
        
        preview_link = book_data['volumeInfo']['previewLink']

        book_detail = {
            'title':title,
            'author':author,
            'cover_image_url':cover_image_url, 
            'preview_url' : preview_link
        }

        return book_detail


@router.get("/suggest")
async def suggest_book(q : str):
    if q[-1] != '.':
        q += '.'

    prompt = "Recommend a book title and how it helps seperated by '|' without author name according to:\n" + q + "\n Give output 'err' if query is not proper" + '\n\n book title:'   
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

    suggested_book = response['choices'][0]['message']['content']
    suggested_book = suggested_book.replace("'s", 's').replace('"','')
    
    if suggested_book == 'err':
        raise HTTPException(status_code=404, detail='Please provide proper query')
    
    book_title_helps = suggested_book.split('|')
    title = book_title_helps[0]
    book_data = get_book_detail(title)
    book_data['description'] = book_title_helps[1]
    
    if book_data:
        return book_data
    
    else:
        raise HTTPException(status_code=404, detail='Please provide proper query')

@router.get("/suggest-many")
def suggest_books(q : str, db:Session = Depends(get_db)):
    q = q.strip()
    db_book_search = get_book_search_by_query(db, q)

    if not db_book_search: # Data does not exists
        db_book_search = BookSearch(query=q)

        # Open AI suggestion
        prompt = q + " Suggest book titles without author name in a single quoted python list according to my query."
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

        # Serializing response
        books = response['choices'][0]['message']['content']
        books = books.replace("'s", 's')

        try:
            suggested_books_title =  eval(books)
        except:
            raise HTTPException(status_code=404, detail='Provide proper query')

        for book_title in suggested_books_title:
                book = get_book_detail(book_title)
                # Adds book detail to db
                db_book = get_book_by_title(db, book['title'])
                if not db_book: # Book doesn't exist in db
                    db_book = Book(title=book['title'], author=book['author'], preview_url=book['preview_url'], cover_image_url=book['cover_image_url'])
                
                db_book_search.books.append(db_book)
    
        db.add(db_book_search)
        db.commit()
        db.refresh(db_book_search)

    return db_book_search.books


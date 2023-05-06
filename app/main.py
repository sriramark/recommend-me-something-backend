from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import books

origins = ['*']

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_methods=['GET']
)

app.include_router(books.router)

@app.get("/")
def read_root():
    return {"README":"API for wisepick"}

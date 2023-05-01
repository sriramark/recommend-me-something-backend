from fastapi import FastAPI
from routers import books

app = FastAPI()

app.include_router(books.router)

@app.get("/")
def read_root():
    return {"README":"API for wisepick"}

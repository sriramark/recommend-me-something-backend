from pydantic import BaseModel

class BookBase(BaseModel):
    title : str
    author : str | None = None
    cover_image_url : str | None = None
    preview_url : str | None = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id : int

    class Config:
        orm_mode = True



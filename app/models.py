from sqlalchemy import  Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship, Mapped

from .database import Base

association_table = Table(
    "book_searches_books",
    Base.metadata,
    Column("book_search_id", ForeignKey("book_searches.id")),
    Column("book_id", ForeignKey("books.id")),
)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    author = Column(String)
    cover_image_url = Column(String(2048))
    preview_url = Column(String(2048))


class BookSearch(Base):
    __tablename__ = "book_searches"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(256))
    search_count = Column(Integer)

    books: Mapped[list[Book]] = relationship(secondary=association_table)


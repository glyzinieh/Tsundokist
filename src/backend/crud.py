from sqlmodel import Session

from .models import Book, User, UserBook


def add_book(session: Session, isbn: str, title: str, author: str):
    book = Book(isbn=isbn, title=title, author=author)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

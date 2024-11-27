from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..crud import add_book
from ..database import get_session
from ..schemas import BookCreate, BookRead

router = APIRouter()


@router.post("/", response_model=BookRead)
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    new_book = add_book(session, book.isbn, book.title, book.author)
    return new_book

from fastapi_users import schemas
from pydantic import BaseModel


class UserCreate(schemas.BaseUserCreate):
    email: str
    role: str


class UserRead(schemas.BaseUser[str]):
    email: str
    role: str


class BookCreate(BaseModel):
    isbn: str
    title: str
    author: str


class BookRead(BaseModel):
    id: int
    isbn: str
    title: str
    author: str

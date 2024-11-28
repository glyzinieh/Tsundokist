from .models import UserBase

class UserPublic(UserBase):
    id: int
    role: str


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    email: str | None = None
    username: str | None = None
    password: str | None = None

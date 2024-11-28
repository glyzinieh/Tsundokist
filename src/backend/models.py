from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    email: str = Field(index=True, unique=True)
    name: str


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    hashed_password: str
    role: str = "user"


class Token(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token: str
    created_at: datetime = Field(default=datetime.now(timezone.utc))

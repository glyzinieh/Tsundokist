import os

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication.strategy.db import (AccessTokenDatabase,
                                                      DatabaseStrategy)
from fastapi_users_db_sqlmodel import SQLModelUserDatabase
from sqlmodel import Session

from ..database import get_session
from ..models import AccessToken, User
from ..schemas import UserCreate, UserRead
from .database import AccessTokenDatabase

SECRET_KEY = os.getenv("SECRET_KEY")

bearer_transport = BearerTransport(tokenUrl="/auth/token")


def get_access_token_db():
    session = next(get_session())
    yield AccessTokenDatabase(AccessToken, session)


def get_database_strategy() -> DatabaseStrategy:
    access_token_db = next(get_access_token_db())
    return DatabaseStrategy(
        secret=SECRET_KEY, lifetime_seconds=3600, token_db=access_token_db
    )


auth_backend = AuthenticationBackend(
    name="bearer",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)


def get_user_db():
    session = next(get_session())
    yield SQLModelUserDatabase(User, session)


fastapi_users = FastAPIUsers(
    get_user_db,
    [auth_backend]
)

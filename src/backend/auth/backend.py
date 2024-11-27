import os

from fastapi import Depends
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication.strategy.db import (AccessTokenDatabase,
                                                      DatabaseStrategy)
from fastapi_users_db_sqlmodel import SQLModelUserDatabase
from fastapi_users_db_sqlmodel.access_token import SQLModelAccessTokenDatabase

from ..database import SessionDep
from ..models import AccessToken, User


def get_user_db():
    yield SQLModelUserDatabase(SessionDep, User)


bearer_transport = BearerTransport("auth/token")


def get_access_token_db():
    yield SQLModelAccessTokenDatabase(SessionDep, AccessToken)


def get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)


SECRET = os.getenv("SECRET_KET")

auth_backend = AuthenticationBackend(
    name="database",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)

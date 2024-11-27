import os
import uuid

from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin

from ..models import User
from .backend import get_user_db

SECRET = os.getenv("SECRET_KEY")


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

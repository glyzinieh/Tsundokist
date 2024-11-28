import os
from contextlib import contextmanager

from fastapi import HTTPException
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlmodel import Session, select
from starlette.requests import Request

from .auth import (authenticate_user, create_tokens, get_user,
                   verify_access_token)
from .database import get_session
from .models import RefreshToken, User


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form.get("username"), form.get("password")
        with next(get_session()) as session:
            user = authenticate_user(email, password, session)
            if not user:
                return False
            access_token, refresh_token = create_tokens(user, session)
            request.session.update(
                {"access_token": access_token, "refresh_token": refresh_token}
            )
            return True

    async def logout(self, request: Request) -> None:
        refresh_token = request.session.get("refresh_token")
        if not refresh_token:
            return False
        with next(get_session()) as session:
            token_db = session.exec(
                select(RefreshToken).where(RefreshToken.token == refresh_token)
            ).first()
            if not token_db:
                return False
            session.delete(token_db)
            session.commit()
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        access_token = request.session.get("access_token")
        if not access_token:
            return False
        email = verify_access_token(access_token)
        with next(get_session()) as session:
            user = get_user(email, session)
            if not user or user.role != "admin":
                return False
        return True


SECRET_KEY = os.getenv("SECRET_KEY")
authentication_backend = AdminAuth(secret_key=SECRET_KEY)


class UserView(ModelView, model=User):
    column_list = [User.id, User.email, User.name, User.is_verified, User.role]


class RefreshTokenView(ModelView, model=RefreshToken):
    column_list = [RefreshToken.id, RefreshToken.user_id, RefreshToken.created_at]

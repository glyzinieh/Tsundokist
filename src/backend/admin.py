import os

from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlmodel import select
from starlette.requests import Request

from .auth import (authenticate_user, create_tokens, get_user, refresh_tokens,
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
        request.session.clear()
        if not refresh_token:
            return True
        with next(get_session()) as session:
            token_db = session.exec(
                select(RefreshToken).where(RefreshToken.token == refresh_token)
            ).first()
            if not token_db:
                return True
            session.delete(token_db)
            session.commit()
        return True

    async def authenticate(self, request: Request) -> bool:
        access_token = request.session.get("access_token")
        if not access_token:
            return False
        email = verify_access_token(access_token)
        if not email:
            if not await self.refresh(request):
                return False
            access_token = request.session.get("access_token")
            email = verify_access_token(access_token)
            if not email:
                return False
        with next(get_session()) as session:
            user = get_user(email, session)
            if not user or user.role != "admin":
                return False
        return True

    async def refresh(self, request: Request) -> bool:
        refresh_token = request.session.get("refresh_token")
        if not refresh_token:
            return False
        with next(get_session()) as session:
            new_access_token, new_refresh_token = refresh_tokens(refresh_token, session)
            if not new_access_token or not new_refresh_token:
                return False
            request.session.update(
                {"access_token": new_access_token, "refresh_token": new_refresh_token}
            )
        return True


SECRET_KEY = os.getenv("SECRET_KEY")
authentication_backend = AdminAuth(secret_key=SECRET_KEY)


class UserView(ModelView, model=User):
    column_list = [User.id, User.email, User.name, User.is_verified, User.role]


class RefreshTokenView(ModelView, model=RefreshToken):
    column_list = [
        RefreshToken.id,
        RefreshToken.user_id,
        RefreshToken.created_at,
        RefreshToken.expires_at,
    ]

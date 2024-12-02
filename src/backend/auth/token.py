import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from sqlmodel import select

from ..database import SessionDep
from ..models import RefreshToken, User

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))


def generate_tokens(user: User):
    now = datetime.now(timezone.utc)

    access_token_payload = {"sub": user.email}
    access_token_expires = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_payload.update({"exp": access_token_expires})
    access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm=ALGORITHM)

    refresh_token_payload = {"sub": user.email}
    refresh_token_expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_payload.update({"exp": refresh_token_expires})
    refresh_token = jwt.encode(refresh_token_payload, SECRET_KEY, algorithm=ALGORITHM)

    return access_token, refresh_token


def create_tokens(user: User, session: SessionDep):
    access_token, refresh_token = generate_tokens(user)

    refresh_token_db = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    session.add(refresh_token_db)
    session.commit()

    return access_token, refresh_token


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def refresh_tokens(token: str, session: SessionDep):
    old_token_db = session.exec(
        select(RefreshToken).where(RefreshToken.token == token)
    ).first()
    if not old_token_db:
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    if old_token_db.expires_at.replace(tzinfo=timezone.utc) < datetime.now(
        timezone.utc
    ):
        raise HTTPException(status_code=400, detail="Refresh token expired")

    user = session.get(User, old_token_db.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    access_token, refresh_token = generate_tokens(user)

    token_db = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    session.delete(old_token_db)
    session.add(token_db)
    session.commit()

    return access_token, refresh_token


def revoke_token(token: str, session: SessionDep):
    token_db = session.exec(
        select(RefreshToken).where(RefreshToken.token == token)
    ).first()
    if not token_db:
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    session.delete(token_db)
    session.commit()
    return True

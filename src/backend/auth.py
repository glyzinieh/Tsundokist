import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import select

from .database import SessionDep
from .models import Token, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(email: str, session: SessionDep):
    return session.exec(select(User).where(User.email == email)).first()


def authenticate_user(email: str, password: str, session: SessionDep):
    user = get_user(email, session)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, session: SessionDep):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        db_token = session.exec(select(Token).where(Token.token == token)).first()
        if not db_token:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

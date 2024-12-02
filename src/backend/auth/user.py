from passlib.context import CryptContext
from sqlmodel import select

from ..database import SessionDep
from ..models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(email: str, session: SessionDep):
    return session.exec(select(User).where(User.email == email)).first()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(email: str, password: str, session: SessionDep):
    user = get_user(email, session)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

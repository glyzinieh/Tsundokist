from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..auth import get_current_user, get_password_hash
from ..database import SessionDep, get_session
from ..models import User
from ..schemas import UserCreate, UserPublic, UserUpdate

router = APIRouter()


@router.post("/", response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep = SessionDep()):
    user = UserCreate.model_validate(user)
    hashed_password = get_password_hash(user.password)
    db_user = User(**user.model_dump(), hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    user: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: SessionDep = SessionDep(),
):
    user_data = user.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.delete("/me", response_model=UserPublic)
def delete_user_me(
    current_user: User = Depends(get_current_user),
    session: SessionDep = SessionDep(),
):
    session.delete(current_user)
    session.commit()
    return current_user

from fastapi import APIRouter, Depends, HTTPException

from ..auth import get_password_hash, oauth2_scheme
from ..database import SessionDep
from ..models import User
from ..schemas import UserCreate, UserPublic, UserUpdate

router = APIRouter()


@router.post("/", response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    user = UserCreate.model_validate(user)
    hashed_password = get_password_hash(user.password)
    db_user = User(**user.model_dump(), hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/{user_id}", response_model=UserPublic)
def read_user(
    user_id: int, session: SessionDep, token: str = Depends(oauth2_scheme)
) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user: UserUpdate, session: SessionDep, token: str = Depends(oauth2_scheme)):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@router.delete("/{user_id}")
def delete_user(user_id: int, session: SessionDep, token: str = Depends(oauth2_scheme)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return user

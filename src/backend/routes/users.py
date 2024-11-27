# from typing import Annotated

# from fastapi import APIRouter, HTTPException, Query
# from passlib.context import CryptContext
# from sqlmodel import select

# from ..database import SessionDep
# from ..models import User
# from ..schemas import UserCreate, UserPublic, UserUpdate

# router = APIRouter()

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# @router.post("/", response_model=UserPublic)
# def create_user(user: UserCreate, session: SessionDep):
#     db_user = User.model_validate(user)
#     hashed_password = pwd_context.hash(db_user.password)
#     db_user.hashed_password = hashed_password
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)
#     return db_user


# @router.get("/", response_model=list[UserPublic])
# def read_users(
#     session: SessionDep,
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 100,
# ) -> list[User]:
#     users = session.exec(select(User).offset(offset).limit(limit)).all()
#     return users


# @router.get("/{user_id}", response_model=UserPublic)
# def read_user(user_id: int, session: SessionDep) -> User:
#     user = session.get(User, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


# @router.patch("/{user_id}", response_model=UserPublic)
# def update_user(user_id: int, user: UserUpdate, session: SessionDep):
#     user_db = session.get(User, user_id)
#     if not user_db:
#         raise HTTPException(status_code=404, detail="User not found")
#     user_data = user.model_dump(exclude_unset=True)
#     if "password" in user_data:
#         user_data["hashed_password"] = pwd_context.hash(user_data.pop("password"))
#     user_db.sqlmodel_update(user_data)
#     session.add(user_db)
#     session.commit()
#     session.refresh(user_db)
#     return user_db


# @router.delete("/{user_id}")
# def delete_user(user_id: int, session: SessionDep):
#     user = session.get(User, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     session.delete(user)
#     session.commit()
#     return user

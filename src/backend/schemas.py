import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    name: str
    role: str


class UserCreate(schemas.BaseUserCreate):
    name: str
    role: str


class UserUpdate(schemas.BaseUserUpdate):
    name: str
    role: str

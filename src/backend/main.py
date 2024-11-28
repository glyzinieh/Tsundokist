from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqladmin import Admin

from .admin import RefreshTokenView, UserView, authentication_backend
from .database import create_db_and_tables, engine
from .routes import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])

admin = Admin(app, engine, authentication_backend=authentication_backend)
# admin = Admin(app, engine)

admin.add_view(UserView)
admin.add_view(RefreshTokenView)

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .auth import fastapi_users, auth_backend
from .database import init_db
from .env import load_env
from .routes import books

load_env()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

# admin = Admin(app, engine)


@app.middleware("http")
async def maintenance_mode(request: Request, call_next):
    if os.getenv("MAINTENANCE_MODE", "False") == "True":
        return JSONResponse(status_code=503, content={"message": "Maintenance mode"})
    return await call_next(request)


app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["Auth"])

app.include_router(books.router, prefix="/books", tags=["Books"])

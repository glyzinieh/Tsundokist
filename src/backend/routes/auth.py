from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..auth import (authenticate_user, create_tokens, refresh_tokens,
                    revoke_token)
from ..database import SessionDep

router = APIRouter()


@router.post("/token")
def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token, refresh_token = create_tokens(user, session)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh(session: SessionDep, rtoken: str = Annotated[str, "refresh_token"]):
    atoken, rtoken = refresh_tokens(rtoken, session)
    return {
        "access_token": atoken,
        "refresh_token": rtoken,
        "token_type": "bearer",
    }


@router.post("/revoke")
def revoke(session: SessionDep, refresh_token: str = Annotated[str, "refresh_token"]):
    if not revoke_token(refresh_token, session):
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    return {"detail": "Token revoked"}

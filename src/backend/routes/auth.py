from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..auth import authenticate_user, create_token
from ..database import SessionDep

router = APIRouter()


@router.post("/token")
def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

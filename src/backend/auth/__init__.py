from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from ..database import SessionDep
from .token import verify_access_token
from .user import get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme), session: SessionDep = SessionDep()
):
    email = verify_access_token(token)
    user = get_user(email, session)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


from .token import (create_tokens, generate_tokens, refresh_tokens,
                    revoke_token, verify_access_token)
from .user import (authenticate_user, get_password_hash, get_user,
                   verify_password)

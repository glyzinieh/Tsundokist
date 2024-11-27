from fastapi_users import models
from fastapi_users_db_sqlmodel import SQLModelBaseUserDB
from fastapi_users_db_sqlmodel.access_token import SQLModelBaseAccessToken



class User(SQLModelBaseUserDB, table=True):
    name: str
    role: str


class AccessToken(SQLModelBaseAccessToken, table=True):
    pass

from typing import Annotated, Union
from typing_extensions import Annotated

from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.param_functions import Form



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authentication")


class OAuth2RequestForm(OAuth2PasswordRequestForm):
        
    def __init__(self, username: str, password: str):
        super().__init__(username=username, password=password)
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer



class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


oauth2_scheme_accsess = OAuth2PasswordBearer(tokenUrl="/authentication")

oauth2_scheme_refresh = OAuth2PasswordBearer(tokenUrl="/refresh")

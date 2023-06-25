from uuid import UUID

from fastapi.exceptions import HTTPException
from pydantic import BaseModel, validator, EmailStr
from pydantic.types import Optional, Union
from pydantic import constr



PATTERN_FOR_LOGIN = ...
PATTERN_FOR_NAME = ...
PATTERN_FOR_PASSWORD = ...


class BaseResponseModel(BaseModel):
    class Config:
        orm_mode = True


class LoginStr(BaseModel, str):

    login: str

    @validator("login")
    def validate_name(cls, value):
        if not PATTERN_FOR_LOGIN.match(value):
            raise HTTPException(
                status_code=422, detail="Login should contains only letters or numbers"
            )
        return value


class ResponseUserModel(BaseResponseModel):

    login: LoginStr
    email: EmailStr
    name: str


class ResponseUserLogin(BaseResponseModel):

    login: LoginStr


class RequestUser(BaseModel):

    username: Union[LoginStr, EmailStr]

    @property
    def is_email(self):
        return type(self.username) is EmailStr


class UserUpdateRequest(BaseModel):
    
    login: Optional[LoginStr]
    name: Optional[constr(min_length=1)]
    email: Optional[EmailStr]

    @validator("name")
    def validate_name(cls, value):
        if not PATTERN_FOR_NAME.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value


class UserCreateRequest(UserUpdateRequest):

    password: str

    @validator("password")
    def validate_password(cls, value):
        if not PATTERN_FOR_PASSWORD.match(value):
            raise HTTPException(
                status_code=422, detail="Password is not valid"
            )
        return value
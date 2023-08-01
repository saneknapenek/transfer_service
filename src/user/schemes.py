import re
from uuid import UUID
from typing import Optional
from enum import Enum

from fastapi.exceptions import HTTPException
from pydantic import BaseModel, EmailStr, field_validator, constr

from src.auth.hashing import Hasher

from src.db.models import ROLES



PATTERN_FOR_NAME = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")
# PATTERN_FOR_EMAIL = re.compile(r"^((([0-9A-Za-z]{1}[-0-9A-z\.]{1,}[0-9A-Za-z]{1})|([0-9А-Яа-я]{1}[-0-9А-я\.]{1,}[0-9А-Яа-я]{1}))@([-A-Za-z]{1,}\.){1,2}[-A-Za-z]{2,})$")
PATTERN_FOR_PASSWORD_LOWWER = re.compile(r"[a-z]+")
PATTERN_FOR_PASSWORD_UPPER = re.compile(r"[A-Z]+")
PATTERN_FOR_PASSWORD_NUMBER = re.compile(r"[0-9]+")
PATTERN_FOR_LOGIN = re.compile(r"^[a-zA-Z_\d]+$")


class BaseResponseModel(BaseModel):
    class Config:
        from_attributes = True


class ResponseUserModel(BaseResponseModel):

    id: UUID
    login: str
    email: EmailStr
    name: str


class ResponseUserExtended(ResponseUserModel):

    role: ROLES


class Email(BaseModel):

    email: EmailStr


class UserUpdateRequest(BaseModel):
    
    login: Optional[str]
    name: Optional[constr(min_length=2)]
    email: Optional[EmailStr]

    @field_validator("name")
    def validate_name(cls, value):
        if not PATTERN_FOR_NAME.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        if len(value) < 1:
            raise HTTPException(
                status_code=422, detail="Name must contain at least two characters"
            )
        return value

    @field_validator("login")
    def validate_login(cls, value):
        if not PATTERN_FOR_LOGIN.match(value):
            raise HTTPException(
                status_code=422, detail="Login must contain only latin letters, numbers, and underscores"
            )
        if len(value) < 2:
            raise HTTPException(
                status_code=422, detail="Login must contain at least three characters"
            )
        return value


class UserCreateRequest(UserUpdateRequest):

    login: str
    name: constr(min_length=1)
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        if not PATTERN_FOR_PASSWORD_NUMBER.search(value):
            raise HTTPException(
                status_code=422, detail="String contains at least one number"
            )
        if not PATTERN_FOR_PASSWORD_LOWWER.search(value):
            raise HTTPException(
                status_code=422, detail="String contains at least one lowercase Latin letter"
            )
        if not PATTERN_FOR_PASSWORD_UPPER.search(value):
            raise HTTPException(
                status_code=422, detail="String contains at least one uppercase Latin letter"
            )
        if len(value) < 8:
            raise HTTPException(
                status_code=422, detail="Password must contain at least eight characters"
            )
        hashed_password = Hasher.get_password_hash(value)
        return hashed_password


class UserUpdateRole(BaseModel):

    role: ROLES
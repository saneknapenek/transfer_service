import re
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, constr

from auth.hashing import Hasher

from db.models import ROLES
from user.exceptions import FieldValidationError



PATTERN_FOR_NAME = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")
# PATTERN_FOR_EMAIL = re.compile(r"^((([0-9A-Za-z]{1}[-0-9A-z\.]{1,}[0-9A-Za-z]{1})|([0-9А-Яа-я]{1}[-0-9А-я\.]{1,}[0-9А-Яа-я]{1}))@([-A-Za-z]{1,}\.){1,2}[-A-Za-z]{2,})$")
PATTERN_FOR_PASSWORD_LOWWER = re.compile(r"[a-z]+")
PATTERN_FOR_PASSWORD_UPPER = re.compile(r"[A-Z]+")
PATTERN_FOR_PASSWORD_NUMBER = re.compile(r"[0-9]+")
PATTERN_FOR_LOGIN = re.compile(r"^[a-zA-Z_.\d]+$")


class BaseResponseModel(BaseModel):
    class Config:
        from_attributes = True


class ResponseUserModel(BaseResponseModel):

    id: UUID
    login: str
    #is email length checked?
    email: EmailStr
    name: str


class ResponseUserExtended(ResponseUserModel):

    role: ROLES


class Email(BaseModel):

    email: EmailStr


class Password(BaseModel):

    password: str

    @field_validator("password")
    def validate_password(cls, value):
        if not PATTERN_FOR_PASSWORD_NUMBER.search(value):
            raise FieldValidationError(
                loc=["body", "password"],
                msg="String contains at least one number"
            )
        if not PATTERN_FOR_PASSWORD_LOWWER.search(value):
            raise FieldValidationError(
                loc=["body", "password"],
                msg="String contains at least one lowercase Latin letter"
            )
        if not PATTERN_FOR_PASSWORD_UPPER.search(value):
            raise FieldValidationError(
                loc=["body", "password"],
                msg="String contains at least one uppercase Latin letter"
            )
        if len(value) < 8:
            raise FieldValidationError(
                loc=["body", "password"],
                msg="Password must contain at least eight characters"
            )
        hashed_password = Hasher.get_password_hash(value)
        return hashed_password

class UserUpdateRequest(BaseModel):
    
    login: Optional[constr(min_length=2, max_length=30)]
    name: Optional[constr(min_length=2, max_length=30)]
    email: Optional[EmailStr]

    @field_validator("name")
    def validate_name(cls, value):
        if not PATTERN_FOR_NAME.match(value):
            raise FieldValidationError(
                loc=["body", "name"],
                msg="Name should contains only letters"
            )
        if len(value) < 1:
            raise FieldValidationError(
                loc=["body", "name"],
                msg="Name must contain at least two characters"
            )
        return value

    @field_validator("login")
    def validate_login(cls, value):
        if not PATTERN_FOR_LOGIN.match(value):
            raise FieldValidationError(
                loc=["body", "login"],
                msg="Login must contain only latin letters, numbers, and underscores"
            )
        if len(value) < 2:
            raise FieldValidationError(
                loc=["body", "login"],
                msg="Login must contain at least three characters"
            )
        return value


class UserCreateRequest(UserUpdateRequest, Password):

    login: constr(min_length=2, max_length=30)
    name: constr(min_length=2, max_length=30)
    email: EmailStr


class UserUpdateRole(BaseModel):

    role: ROLES

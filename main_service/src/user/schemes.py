import re
from uuid import UUID
from typing import Optional, ClassVar

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
    email: EmailStr
    name: str


class ResponseUserExtended(ResponseUserModel):

    role: ROLES


class Email(BaseModel):

    email: EmailStr

    @staticmethod
    def check_lenght(value):
        return (isinstance(value, str)
                and len(value) <= 75)


class Password(BaseModel):

    MAX_L: ClassVar = 30
    MIN_L: ClassVar = 8

    password: constr(min_length=MIN_L, max_length=MAX_L)

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
        hashed_password = Hasher.get_password_hash(value)
        return hashed_password
    
    @classmethod
    def is_password(cls, value):
        return (isinstance(value, str)
                and cls.MIN_L <= len(value) <= cls.MAX_L
                and PATTERN_FOR_PASSWORD_NUMBER.search(value)
                and PATTERN_FOR_PASSWORD_LOWWER.search(value)
                and PATTERN_FOR_PASSWORD_UPPER.search(value))
    

class Login(BaseModel):

    MAX_L: ClassVar = 50
    MIN_L: ClassVar = 2

    login: constr(min_length=MIN_L, max_length=MAX_L)

    @field_validator("login")
    def validate_login(cls, value):
        if not PATTERN_FOR_LOGIN.match(value):
            raise FieldValidationError(
                loc=["body", "login"],
                msg="Login must contain only latin letters, numbers, and underscores"
            )
        return value

    @classmethod
    def is_login(cls, value):
        return (isinstance(value, str)
                and cls.MIN_L <= len(value) <= cls.MAX_L
                and PATTERN_FOR_LOGIN.match(value))


class Name(BaseModel):

    MAX_L: ClassVar = 50
    MIN_L: ClassVar = 2


    name: constr(min_length=MIN_L, max_length=MAX_L)

    @field_validator("name")
    def validate_name(cls, value):
        if not PATTERN_FOR_NAME.match(value):
            raise FieldValidationError(
                loc=["body", "name"],
                msg="Name should contains only letters"
            )
        return value


class UserCreateRequest(Login, Name, Email, Password):
    pass


class UserUpdateRequest(Login, Name, Email):
    
    login: Optional[constr(min_length=Login.MIN_L, max_length=Login.MAX_L)]
    name: Optional[constr(min_length=Name.MIN_L, max_length=Name.MAX_L)]
    email: Optional[EmailStr]


class UserUpdateRole(BaseModel):

    role: ROLES

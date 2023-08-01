from typing import Any, Dict, Optional
from fastapi import HTTPException, status



class UserNotFound(HTTPException):
    
    def __init__(self, headers: dict[str, str] | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
            headers=headers
        )


class NotEnoughRights(HTTPException):

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough rights.",
            headers=None
        )


class UserDeactivate(HTTPException):

    def __init__(self, headers: dict[str, str] | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_410_GONE,
            detail="User has been deleted.",
            headers=None
        )


class Unauthorized(HTTPException):

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )


class UserAlreadyExists(HTTPException):

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with the same username or email already exists.",
            headers=None
        )
        

class IncorrectPassword(HTTPException):

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect old password",
            headers=None
        )
        

class MatchingPasswords(HTTPException):

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Old and new password must not match",
            headers=None
        )
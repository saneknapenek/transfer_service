from fastapi import HTTPException, status



class UserNotFound(HTTPException):
    
    def __init__(self, headers: dict[str, str] | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "msg": "User not found"
            },
            headers=headers
        )


class NotEnoughRights(HTTPException):

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "msg": "Not enough rights"
            },
            headers=None
        )


class UserDeactivate(HTTPException):

    def __init__(self, headers: dict[str, str] | None = None) -> None:
        super().__init__(
            status_code=status.HTTP_410_GONE,
            detail={
                "msg": "User has been deleted"
            },
            headers=None
        )


class Unauthorized(HTTPException):

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "msg": "Incorrect username or password"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )


class UserAlreadyExists(HTTPException):

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "msg": "A user with the same username or email already exists"
            },
            headers=None
        )
        

class IncorrectPassword(HTTPException):

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "msg": "Incorrect old password"
            },
            headers=None
        )
        

class MatchingPasswords(HTTPException):

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "msg": "Old and new password must not match"
            },
            headers=None
        )


class FieldValidationError(HTTPException):

    def __init__(self, loc: list, msg: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "loc": loc,
                "msg": msg
            }
        )
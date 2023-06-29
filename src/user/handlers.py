from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError

from database import get_db_session
from .actions import _create_user, _delete_user, _update_user, _get_user_by_email, _get_user_by_login
from .schemes import ResponseUserModel, RequestUser, UserCreateRequest, UserUpdateRequest, ResponseUserLogin, LoginStr
from .exceptions import UserNotFound


user_router = APIRouter()


@user_router.get("/", response_model=ResponseUserModel)
async def get_user(username: RequestUser, session: AsyncSession = Depends(get_db_session)) -> ResponseUserModel:
    
    if username.username.is_email():
        user = await _get_user_by_email(str, session)
    else:
        user = await _get_user_by_login(str, session)
    if user is None:
        raise UserNotFound
    return ResponseUserModel(
            login=user.login,
            name=user.name,
            email=user.email
        )

@user_router.post("/", response_model=ResponseUserModel)
async def create_user(body: UserCreateRequest, session: AsyncSession = Depends(get_db_session)) -> ResponseUserModel:

    try:
        user = await _create_user(body, session)
    except IntegrityError as exp:
        if "UniqueViolationError" in str(exp):
            raise HTTPException(
                status_code=403, detail="User with this email already exists"
            )
        else:
            raise exp
    return ResponseUserModel(
            login=user.login,
            name=user.name,
            email=user.email
        )

@user_router.patch("/", response_model=ResponseUserModel)
async def update_user(login: LoginStr, body: UserUpdateRequest, session: AsyncSession = Depends(get_db_session)) -> ResponseUserModel:

    updating_params = body.dict(exclude_none=True)
    if not updating_params:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter must be present"
        )
    updated_user = await _update_user(login, updating_params, session)
    if updated_user is None:
        raise UserNotFound
    return ResponseUserModel(
        login=updated_user.login,
        name=updated_user.name,
        email=updated_user.email
    )

@user_router.delete("/", response_model=ResponseUserLogin)
async def delete_user(login: LoginStr, session: AsyncSession = Depends(get_db_session)) -> ResponseUserLogin:

    deleted_user = await _delete_user(login, session)
    if deleted_user is None:
        raise UserNotFound
    return ResponseUserLogin(
        login=deleted_user
    )

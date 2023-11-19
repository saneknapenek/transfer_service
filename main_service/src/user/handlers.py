from typing import Annotated
from uuid import UUID

from auth.schemes import Token
from auth.security import (
    authenticate_user,
    create_tokens,
    get_current_user,
    replacement,
)
from db.models import ROLES, User
from db.repositories.user import UserAlchemy
from db.settings import get_db_session
from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from user.exceptions import (
    IncorrectPassword,
    MatchingPasswords,
    NotEnoughRights,
    Unauthorized,
    UserAlreadyExists,
    UserDeactivate,
    UserNotFound,
)
from user.schemes import (
    Email,
    Login,
    Password,
    ResponseUserExtended,
    ResponseUserModel,
    UserCreateRequest,
    UserUpdateRequest,
    UserUpdateRole,
)

user_router = APIRouter(tags=["user"])


@user_router.get("/", response_model=ResponseUserModel)
async def get_user(id: UUID, session: Annotated[AsyncSession, Depends(get_db_session)],
                   current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role == ROLES.USER and id != current_user.id:
        raise NotEnoughRights
    response = await UserAlchemy(session=session).get(id)
    if response is None:
        raise UserNotFound
    return response.dict()

@user_router.patch("/", response_model=ResponseUserModel)
async def update_user(id: UUID, data: UserUpdateRequest,
                      session: Annotated[AsyncSession, Depends(get_db_session)],
                      current_user=Depends(get_current_user)):
    if current_user.role == ROLES.USER and id != current_user.id:
        raise NotEnoughRights
    if current_user.role == ROLES.SUPER_USER and current_user.id != id:
        user = await UserAlchemy(session).get(id)
        if user is None:
            raise UserNotFound
        if user.role in (ROLES.SUPER_USER, ROLES.ADMIN):
            raise NotEnoughRights
    response = await UserAlchemy(session=session).update(data=data.model_dump(exclude_none=True), id=id)
    if response is None:
        raise UserNotFound
    return response.dict()

@user_router.delete("/", response_model=UUID)
async def deactivate_user(id: UUID,
                          session: Annotated[AsyncSession, Depends(get_db_session)],
                          current_user=Depends(get_current_user)):
    if current_user.role == ROLES.USER and id != current_user.id:
        raise NotEnoughRights
    if current_user.role == ROLES.SUPER_USER and id != current_user.id:
        user = await UserAlchemy(session).get(id)
        if user.role in (ROLES.SUPER_USER, ROLES.ADMIN):
            raise NotEnoughRights
    response = await UserAlchemy(session=session).deactivate(id)
    if response is None:
        raise UserNotFound
    return response

@user_router.patch("/password", response_model=ResponseUserModel)
async def change_password(old_password: Annotated[str, Form()],
                          new_password: Annotated[str, Form()],
                          session: Annotated[AsyncSession, Depends(get_db_session)],
                          current_user=Depends(get_current_user)):
    if old_password == new_password:
        raise MatchingPasswords
    new_password = Password(password=new_password).password
    user = await authenticate_user(password=old_password, session=session, username=current_user.username)
    if user is None:
        raise IncorrectPassword
    response = await UserAlchemy(session).update(id=current_user.id, data={"password": new_password})
    return response.dict()


admin_router = APIRouter(prefix="/hidden", tags=["admin"])


@admin_router.patch("/assign", response_model=ResponseUserExtended)
async def assign_role(id: UUID,
                      data: UserUpdateRole,
                      session: Annotated[AsyncSession, Depends(get_db_session)],
                      current_user=Depends(get_current_user)):
    if current_user.role != ROLES.ADMIN:
        raise NotEnoughRights
    response = await UserAlchemy(session).update(id=id, data=data.model_dump())
    return response.dict()

@admin_router.delete("/delete", response_model=UUID)
async def delete_user(id: UUID, session: Annotated[AsyncSession, Depends(get_db_session)],
                      current_user=Depends(get_current_user)):
    if current_user.role == ROLES.USER:
        raise NotEnoughRights
    if current_user.role == ROLES.SUPER_USER:
        user = await UserAlchemy(session).get(id)
        if user is None:
            raise UserNotFound
        if user.role is (ROLES.SUPER_USER, ROLES.ADMIN):
            raise NotEnoughRights
    response = await UserAlchemy(session).delete(id)
    return response


auth_router = APIRouter(tags=["auth"])


@auth_router.post("/authentication", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db_session)]
):    
    if Password.is_password(form_data.password):
        if Login.is_login(form_data.username):
            user = await authenticate_user(username=form_data.username, password=form_data.password, session=session)
        elif Email.check_lenght(form_data.username):
            user = await authenticate_user(email=form_data.username, password=form_data.password, session=session)
        else:
            raise Unauthorized
    else:
        raise Unauthorized
    if user is None:
        raise Unauthorized
    if not user.is_active:
        raise UserDeactivate
    tokens = await create_tokens(data={"sub": user.username})
    return tokens

@auth_router.post("/registration", response_model=ResponseUserModel)
async def registration(data: UserCreateRequest, session: Annotated[AsyncSession, Depends(get_db_session)]):
    result = await UserAlchemy(session=session).create(data=data.model_dump())
    return result.dict()

@auth_router.post("/refresh")
async def refresh_token(token=Depends(replacement)):
    return token

@auth_router.post("/currentuser", response_model=ResponseUserExtended)
async def get_current_user(current_user=Depends(get_current_user)):
    return current_user
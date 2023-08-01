from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.db.models import User

from src.auth.env import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from src.auth.security import authenticate_user, get_current_user, replacement, create_tokens
from src.auth.schemes import Token

# from .actions import _create_user, _delete_user, _update_user, _get_user_by_email, _get_user_by_login
from .schemes import ResponseUserModel, RequestUser, UserCreateRequest, UserUpdateRequest, ResponseUserLogin
from .exceptions import UserNotFound



user_router = APIRouter(tags=["user"])


# @user_router.get("/", response_model=ResponseUserModel)
# async def get_user(username: RequestUser, session: AsyncSession = Depends(get_db_session)) -> ResponseUserModel:
    
#     if username.username.is_email():
#         user = await _get_user_by_email(str, session)
#     else:
#         user = await _get_user_by_login(str, session)
#     if user is None:
#         raise UserNotFound
#     return ResponseUserModel(
#             login=user.login,
#             name=user.name,
#             email=user.email
#         )

# @user_router.post("/", response_model=ResponseUserModel)
# async def create_user(body: UserCreateRequest, session: AsyncSession = Depends(get_db_session)) -> ResponseUserModel:

#     try:
#         user = await _create_user(body, session)
#     except IntegrityError as exp:
#         if "UniqueViolationError" in str(exp):
#             raise HTTPException(
#                 status_code=403, detail="User with this email already exists"
#             )
#         else:
#             raise exp
#     return ResponseUserModel(
#             login=user.login,
#             name=user.name,
#             email=user.email
#         )

# @user_router.patch("/", response_model=ResponseUserModel)
# async def update_user(login: LoginStr, body: UserUpdateRequest, session: AsyncSession = Depends(get_db_session)) -> ResponseUserModel:

#     updating_params = body.dict(exclude_none=True)
#     if not updating_params:
#         raise HTTPException(
#             status_code=422,
#             detail="At least one parameter must be present"
#         )
#     updated_user = await _update_user(login, updating_params, session)
#     if updated_user is None:
#         raise UserNotFound
#     return ResponseUserModel(
#         login=updated_user.login,
#         name=updated_user.name,
#         email=updated_user.email
#     )

# @user_router.delete("/", response_model=ResponseUserLogin)
# async def delete_user(login: LoginStr, session: AsyncSession = Depends(get_db_session)) -> ResponseUserLogin:

#     deleted_user = await _delete_user(login, session)
#     if deleted_user is None:
#         raise UserNotFound
#     return ResponseUserLogin(
#         login=deleted_user
#     )


from src.db.repositories.user import UserAlchemy
from src.user.schemes import UserCreateRequest

@user_router.get("/", response_model=ResponseUserModel)
async def get_user(id: str, session: Annotated[AsyncSession, Depends(get_db_session)],
                   current_user: Annotated[User, Depends(get_current_user)]):
    response = await UserAlchemy(session=session).get(current_user.id)
    return response.dict()

@user_router.patch("/", response_model=ResponseUserModel)
async def update_user(data: UserUpdateRequest,
                      session: Annotated[AsyncSession, Depends(get_db_session)],
                      current_user=Depends(get_current_user)):
    response = await UserAlchemy(session=session).update(data=data.model_dump(exclude_none=True), id=current_user.id)
    return response.dict()

@user_router.delete("/", response_model=UUID)
async def delete_user(session: Annotated[AsyncSession, Depends(get_db_session)],
                      current_user=Depends(get_current_user)):
    response = await UserAlchemy(session=session).deactivate(current_user.id)
    return response


auth_router = APIRouter(tags=["auth"])


@auth_router.post("/authentication", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    user = await authenticate_user(form_data.username, form_data.password, session=session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    tokens = await create_tokens(data={"sub": user.username})
    return tokens

@auth_router.post("/registration", response_model=ResponseUserModel)
async def registration(data: UserCreateRequest, session: Annotated[AsyncSession, Depends(get_db_session)]):
    result = await UserAlchemy(session=session).create(data=data.model_dump())
    return result.dict()

@auth_router.post("/refresh")
async def refresh_token(token=Depends(replacement)):
    return token
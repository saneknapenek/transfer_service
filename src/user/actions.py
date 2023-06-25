from typing import Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from .schemes import UserCreate
from db import models
from db import dals



class Hasher:
    pass


async def _create_user(user: UserCreate, session: AsyncSession) -> Union[models.User, None]:
    user_dal = dals.UserDAL(session)
    new_user = await user_dal.create_user(
        name=user.name,
        surname=user.surname,
        email=user.email,
        hashed_password=Hasher.get_password_hash(user.password)
    )
    return new_user

async def _get_user_by_login(login: str, session: AsyncSession) -> Union[models.User, None]:
    user_dal = dals.UserDAL(session)
    user = await user_dal.get_user_by_login(
        email=str(login)
    )
    return user

async def _get_user_by_email(email: EmailStr, session: AsyncSession) -> Union[models.User, None]:
    user_dal = dals.UserDAL(session)
    user = await user_dal.get_user_by_email(
        email=str(email)
    )
    return user

async def _update_user(login: str, updating_params: dict, session: AsyncSession) -> Union[models.User, None]:
    user_dal = dals.UserDAL(session)
    updated_user = await user_dal.update_user(str(login), updating_params)
    return updated_user

async def _delete_user(login: str, session: AsyncSession) -> Union[str, None]:
        user_dal = dals.UserDAL(session)
        user_login = await user_dal.delete_user(str(login))
        return user_login
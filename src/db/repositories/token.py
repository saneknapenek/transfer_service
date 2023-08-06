from uuid import UUID
from typing import Union

from sqlalchemy import select, update
from sqlalchemy.orm import DeclarativeBase

from db.models import UsedTokens
from db.repository import SQLAlchemyRepository
from db.exceptions import MethodNotAllowed



class TokenAlchemy(SQLAlchemyRepository):

    model: UsedTokens = UsedTokens

    async def update(self, *args, **kwargs) -> DeclarativeBase:
        raise MethodNotAllowed

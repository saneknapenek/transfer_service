from uuid import UUID
from typing import Union

from sqlalchemy import select, update
from sqlalchemy.orm import DeclarativeBase

from src.db.models import UsedTokens
from src.db.repository import SQLAlchemyRepository
from src.db.exceptions import MethodNotAllowed



class TokenAlchemy(SQLAlchemyRepository):

    model: UsedTokens = UsedTokens

    async def update(self, *args, **kwargs) -> DeclarativeBase:
        raise MethodNotAllowed
    
    async def get_for_token_id(self, token_id) -> Union[DeclarativeBase, None]:
        stmt = (select(UsedTokens).
                where(UsedTokens.token_id==token_id))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
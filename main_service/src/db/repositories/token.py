from sqlalchemy.orm import DeclarativeBase

from db.models import UsedTokens
from db.repository import SQLAlchemyRepository
from db.exceptions import MethodNotAllowed



class TokenAlchemy(SQLAlchemyRepository):

    model: UsedTokens = UsedTokens

    async def update(self, *args, **kwargs) -> DeclarativeBase:
        raise MethodNotAllowed

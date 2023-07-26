from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.db.repository import SQLAlchemyRepository



class UserAlchemy(SQLAlchemyRepository):

    model: User = User

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_for_username(self, username: str) -> DeclarativeBase:
        stmt = (select(self.model).
                where(self.model.login==username))
        res = await self.session.execute(stmt)
        return res.first()

from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase

from db.models import User
from db.repository import SQLAlchemyRepository



class UserAlchemy(SQLAlchemyRepository):

    model: User = User

    async def get_for_username(self, username: str) -> DeclarativeBase:
        stmt = (select(self.model).
                where(self.model.login==username))
        res = await self.session.execute(stmt)
        return res.first()

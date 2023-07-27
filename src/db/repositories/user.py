from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.db.repository import SQLAlchemyRepository



class UserAlchemy(SQLAlchemyRepository):

    model: User = User

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_for_login(self, login: str) -> DeclarativeBase:
        stmt = (select(self.model).
                where(self.model.login==login))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
    
    async def deactivate(self, id: UUID) -> UUID:
        stmt = (update(self.model).
                where(self.model.id==id).
                values(is_active=False).
                returning(self.model.id))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

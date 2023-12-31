from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import DeclarativeBase

from db.models import User
from db.repository import SQLAlchemyRepository



class UserAlchemy(SQLAlchemyRepository):

    model: User = User

    async def get_for_email(self, email: str) -> DeclarativeBase | None:
        stmt = (select(self.model).
                where(self.model.email==email))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_for_login(self, login: str) -> DeclarativeBase | None:
        stmt = (select(self.model).
                where(self.model.login==login))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
    
    async def deactivate(self, id: UUID) -> UUID | None:
        stmt = (update(self.model).
                where(self.model.id==id).
                values(is_active=False).
                returning(self.model.id))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
    
    async def get_include_services(self, id: UUID) -> dict:
        stmt = (select(self.model, self.model.services).
                where(self.model.id==id).
                join(self.model, self.model.services))
        res = await self.session.execute(stmt)
        return res.scalars().all()

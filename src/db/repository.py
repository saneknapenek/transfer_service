from abc import ABC, abstractmethod

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete
from sqlalchemy.engine import CursorResult



class Repository(ABC):
    
    @abstractmethod
    async def create():
        raise NotImplementedError
    
    @abstractmethod
    async def update():
        raise NotImplementedError
    
    @abstractmethod
    async def delete():
        raise NotImplementedError
    
    @abstractmethod
    async def get():
        raise NotImplementedError
    

class SQLAlchemyRepository(Repository):

    model: DeclarativeBase
    
    async def create(self, data: dict) -> DeclarativeBase:
        stmt = (insert(self.model).
                values(**data).
                returning(self.model))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update(self, id: int, data: dict) -> DeclarativeBase:
        stmt = (update(self.model).
                where(self.model.id==id).
                values(**data).
                returning(self.model))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def delete(self, id: int) -> int:
        stmt = (delete(self.model).
                where(self.model.id==id))
        res = await self.session.execute(stmt)
        return res.context.isdelete

    async def get(self, id: int) -> DeclarativeBase:
        stmt = (select(self.model).
                where(self.model.id==id))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

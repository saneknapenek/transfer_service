from uuid import UUID

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select

from db.models import Media
from db.repository import SQLAlchemyRepository



class MediaAlchemy(SQLAlchemyRepository):

    model = Media

    async def get_all_for_service(self, user: UUID, service: UUID | None) -> list[DeclarativeBase]:
        if service is None:
            stmt = (select(self.model).
                    join(self.model.service.user==user))
        else:
            stmt = (select(self.model).
                    where(self.model.service==service).
                    where(self.model.service.user==user))
        res = await self.session.execute(stmt)
        return res.scalars().all()
    
    async def get_for_service(self, id: UUID, user: UUID, service: DeclarativeBase) -> DeclarativeBase:
        stmt = (select(self.model).
                join(service.__class__, self.model.service_id==service.id).
                where(self.model.id==id))
        res = await self.session.execute(stmt)
        raise ValueError(res.scalars().first())
        # return res.scalars().first()
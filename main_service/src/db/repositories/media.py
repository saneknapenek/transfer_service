from uuid import UUID

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select

from db.models import Media
from db.repository import SQLAlchemyRepository



class MediaAlchemy(SQLAlchemyRepository):

    model = Media

    async def get_for_service(self, user: UUID, service: UUID | None) -> list[DeclarativeBase]:
        if service is None:
            stmt = (select(self.model).
                    join(self.model.service.user==user))
        else:
            stmt = (select(self.model).
                    where(self.model.service==service).
                    where(self.model.service.user==user))
        res = await self.session.execute(stmt)
        return res.scalars().all()
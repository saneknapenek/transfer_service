from uuid import UUID

from sqlalchemy import select, delete

from db.models import Service, SERVICES
from db.repository import SQLAlchemyRepository



class ServiceAlchemy(SQLAlchemyRepository):

    model = Service

    async def get_for_user(self, name: SERVICES,  user_id: UUID) -> Service | None:
        stmt = (select(self.model).
                where(self.model.name==name,
                      self.model.user_id==user_id))
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
    
    async def delete_for_user(self, name: SERVICES, user_id: UUID) -> int:
        stmt = (delete(self.model).
                where(self.model.name==name,
                      self.model.user_id==user_id))
        res = await self.session.execute(stmt)
        return res.context.isdelete

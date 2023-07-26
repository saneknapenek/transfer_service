from db.models import Service
from db.repository import SQLAlchemyRepository



class ServiceAlchemy(SQLAlchemyRepository):

    model = Service
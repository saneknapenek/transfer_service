from db.models import Media
from db.repository import SQLAlchemyRepository



class ServiceAlchemy(SQLAlchemyRepository):

    model = Media
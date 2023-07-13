import uuid
import enum
from datetime import datetime


from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship



Base = declarative_base()


class ROLES(enum.Enum):
    
    USER = 1
    SUPER_USER = 2
    ADMIN = 3


class SERVICES(enum.Enum):

    YANDEX = "yandex"
    GOOGLE = "google"


class ObjectsFromService(Base):
    __tablename__ = "objects_from_service"

    service: str = Column(String, ForeignKey("service.name"))
    objects: str = Column(String, ForeignKey("object.hash"))
    name_on_service: str = Column(String, nullable=False)
    created_on_service: datetime = Column(datetime, nullable=False)
    modified_on_service: datetime = Column(datetime, nullable=False)


class ServicesForUser(Base):
    __tablename__ = "services_for_user"

    user: uuid = Column(UUID, ForeignKey("user.id"))
    service: str = Column(String, ForeignKey("service.name"))
    email: str = Column(String, nullable=False)


class User(Base):
    __tablename__ = "user"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login : str = Column(String, nullable=False, unique=True)
    email: str = Column(String, nullable=False, unique=True)
    name: str = Column(String, nullable=False)
    is_active: bool = Column(Boolean(), default=True)
    hashed_password: str = Column(String, nullable=False)
    role: int = Column(Integer, default=ROLES.USER.value)
    service: str = relationship("Service",
                                secondary=ServicesForUser.__table__,
                                back_populates="user")


class Object(Base):
    __tablename__ = "object"

    hash: str = Column(String, primary_key=True, unique=True)
    datetime_created: datetime = Column(datetime, nullable=False)
    content_type: str = Column(String, nullable=False)
    service = relationship("Service",
                           secondary=ObjectsFromService.__table__,
                           back_populates="object")


class Service(Base):
    __tablename__ = "service"

    name: str = Column(Enum(SERVICES), primary_key=True)
    user: uuid = relationship("User",
                              secondary=ServicesForUser.__table__,
                              back_populates="service")
    objects: str =relationship("Object",
                               secondary=ObjectsFromService.__table__,
                               back_populates="service")

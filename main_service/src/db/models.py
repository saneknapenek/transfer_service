import uuid
import enum
from datetime import datetime


from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty



class ROLES(enum.Enum):
    
    USER = 1
    SUPER_USER = 2
    ADMIN = 3


class SERVICES(enum.Enum):

    YANDEX = "yandex"
    GOOGLE = "google"



class Base(DeclarativeBase):

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True)

    def dict(self) -> dict:
        attributes = {}
        attrs = inspect(self.__class__).attrs
        for column in attrs.values():
            if isinstance(column, ColumnProperty):
                attributes[column.key] = self.__dict__[column.key]
        return attributes


class User(Base):
    __tablename__ = "user"

    login : Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[int] = mapped_column(default=ROLES.USER.value)
    services: Mapped[list["Service"]] = relationship(back_populates="user")

    @property
    def username(self):
        return self.login


class Media(Base):
    __tablename__ = "media"

    hash: Mapped[str] = mapped_column(nullable=False)
    datetime_created: Mapped[datetime] = mapped_column(nullable=False)
    content_type: Mapped[str] = mapped_column(nullable=False)
    name_on_service: Mapped[str] = mapped_column(nullable=False)
    created_on_service: Mapped[datetime] = mapped_column(nullable=False)
    modified_on_service: Mapped[datetime] = mapped_column(nullable=False)
    gps_latitude: Mapped[float] = mapped_column(nullable=True)
    gps_longitude: Mapped[float] = mapped_column(nullable=True)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("service.id"))
    service: Mapped["Service"] = relationship(back_populates="medias")


class Service(Base):
    __tablename__ = "service"

    name: Mapped[str] = mapped_column(default=Enum(SERVICES), primary_key=True, nullable=False)
    token: Mapped[str] = mapped_column(nullable=False)
    user_email: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="services")
    medias: Mapped[list["Media"]] = relationship(back_populates="service")


class UsedTokens(Base):
    __tablename__ = "used_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow())

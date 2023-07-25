import uuid
import enum
from datetime import datetime


from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase



class ROLES(enum.Enum):
    
    USER = 1
    SUPER_USER = 2
    ADMIN = 3


class SERVICES(enum.Enum):

    YANDEX = "yandex"
    GOOGLE = "google"



class Base(DeclarativeBase):

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True)


class User(Base):
    __tablename__ = "user"

    login : Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[int] = mapped_column(default=ROLES.USER.value)
    services: Mapped[list["Service"]] = relationship(back_populates="user")


class Object(Base):
    __tablename__ = "object"

    hash: Mapped[str] = mapped_column(nullable=False)
    datetime_created: Mapped[datetime] = mapped_column(nullable=False)
    content_type: Mapped[str] = mapped_column(nullable=False)
    name_on_service: Mapped[str] = mapped_column(nullable=False)
    created_on_service: Mapped[datetime] = mapped_column(nullable=False)
    modified_on_service: Mapped[datetime] = mapped_column(nullable=False)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("service.id"))
    service: Mapped["Service"] = relationship(back_populates="objects")


class Service(Base):
    __tablename__ = "service"

    name: Mapped[str] = mapped_column(default=Enum(SERVICES), primary_key=True, nullable=False)
    token: Mapped[str] = mapped_column(nullable=False)
    user_email: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="services")
    objects: Mapped[list["Object"]] = relationship(back_populates="service")

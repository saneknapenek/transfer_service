import uuid
from enum import Enum

from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base



Base = declarative_base()


class ROLES(Enum):
    
    USER = 1
    SUPER_USER = 2
    ADMIN = 3


class User(Base):
    __tablename__ = "users"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login : str = Column(String, nullable=False, unique=True)
    email: str = Column(String, nullable=False, unique=True)
    name: str = Column(String, nullable=False)
    is_active: bool = Column(Boolean(), default=True)
    hashed_password: str = Column(String, nullable=False)
    role: int = Column(Integer, default=ROLES.USER.value)

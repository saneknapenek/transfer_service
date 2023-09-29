from typing import Generator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from env import DATABASE_URL


engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=True,
    execution_options={"isolation_level": "AUTOCOMMIT"},
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db_session() -> Generator:
    """Dependency for getting async session"""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
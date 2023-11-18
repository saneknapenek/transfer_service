import asyncio
import uuid
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
# from src.db.settings import get_db_session
from tests.env import (
    DATABASE_HOST,
    DATABASE_PORT,
    POSTGRESE_PASSWORD,
    POSTGRESE_USER,
    TEST_POSTGRES_DB,
)
from httpx import AsyncClient

from src.db import models



TEST_DATABASE_URL = f"postgresql+asyncpg://{POSTGRESE_USER}:{POSTGRESE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{TEST_POSTGRES_DB}"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=True,
    execution_options={"isolation_level": "AUTOCOMMIT"}
    )

async_session_maker = sessionmaker(engine_test, class_=AsyncSession)

metadata = models.Base.metadata
metadata.bind = engine_test

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        session: AsyncSession = async_session_maker()
        yield session
    finally:
        await session.close()


# async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
#     async with async_session_maker() as session:
#         yield session

# app.dependency_overrides[get_db_session] = override_get_async_session


@pytest_asyncio.fixture(autouse=True, scope='function')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)

@pytest.fixture(scope='session')
def event_loop(request: pytest.FixtureRequest):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope='function')
async def client():
    client = AsyncClient(base_url="http://0.0.0.0:8000")
    yield client
    await client.aclose()

@pytest_asyncio.fixture(scope='function')
async def get_test_db_session() -> Generator:
    try:
        session: AsyncSession = async_session_maker()
        yield session
    finally:
        await session.close()

@pytest_asyncio.fixture
async def get_user_by_id(get_test_db_session: AsyncSession):
    async def get_user_from_database(id: uuid.UUID):
        query = select(models.User).where(models.User.id==id)
        res = await get_test_db_session.execute(query)
        return res.scalar_one_or_none()
    return get_user_from_database

@pytest_asyncio.fixture
async def create_user(get_test_db_session: AsyncSession):
    async def create_user_in_db(user_data: dict):
        stmt = insert(models.User).values(**user_data).returning(models.User)
        user = await get_test_db_session.execute(stmt)
        return user.scalar_one_or_none()
    return create_user_in_db

@pytest_asyncio.fixture
async def get_user_by_login(get_test_db_session: AsyncSession):
    async def get_user_from_database(login: str):
        query = select(models.User).where(models.User.login==login)
        res = await get_test_db_session.execute(query)
        return res.scalar_one_or_none()
    return get_user_from_database

@pytest_asyncio.fixture
async def get_user_by_name(get_test_db_session: AsyncSession):
    async def get_user_from_database(name: str):
        query = select(models.User).where(models.User.name==name)
        res = await get_test_db_session.execute(query)
        return res.scalar_one_or_none()
    return get_user_from_database

@pytest_asyncio.fixture
async def get_user_by_email(get_test_db_session: AsyncSession):
    async def get_user_from_database(email: str):
        query = select(models.User).where(models.User.email==email)
        res = await get_test_db_session.execute(query)
        return res.scalar_one_or_none()
    return get_user_from_database
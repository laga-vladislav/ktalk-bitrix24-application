import pytest
import string
import random
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.db.schemes import Base

from httpx import AsyncClient
from src.main import app

from environs import Env
from crest.crest import CRestBitrix24

env = Env()

"""
Настройки базы данных
"""
TEST_URI = "sqlite+aiosqlite:///data/test.sqlite3"

engine_test = create_async_engine(TEST_URI)
async_session_maker = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False)
# Base.metadata.bind = engine_test


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        print("Preparing database...")
        await conn.run_sync(Base.metadata.create_all)
        print("Database is ready")
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def get_random_string(length: int = 10):
    return ''.join(random.choices(string.ascii_uppercase +
                                  string.digits, k=length))


"""
Настройки CRest приложения
"""
webhook = env.str("CLIENT_WEBHOOK")
crest_webhook = CRestBitrix24(client_webhook=webhook)


# """
# Настройки fastapi приложения
# """


# async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
#     async with async_session_maker() as session:
#         yield session

# app.dependency_overrides[get_session] = override_get_session


# @pytest.fixture(scope="session")
# async def ac() -> AsyncGenerator[AsyncClient, None]:
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         yield ac

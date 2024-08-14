import pytest
import string
import random
from typing import AsyncGenerator
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import PortalModel
from src.db.schemes import Base
from src.db.requests import add_portal, get_portal, refresh_portal

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
    # async with engine_test.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def get_random_string(length: int = 10):
    return ''.join(random.choices(string.ascii_uppercase +
                                  string.digits, k=length))


test_portal_data_dict = {
    'member_id': get_random_string(),
    'endpoint': 'endpoint',
    'scope': 'scope',
    'access_token': 'access_token',
    'refresh_token': 'refresh_token',
    # 'updated_at': datetime.now()
}
test_portal_data_model = PortalModel(
    member_id=get_random_string(),
    endpoint='endpoint',
    scope='scope',
    access_token='access_token',
    refresh_token='refresh_token',
    # updated_at=datetime.now()
)


class TestDatabase:
    async def test_add_portal_dict(self, get_session):
        print(test_portal_data_model.member_id)
        await add_portal(get_session, test_portal_data_model)
        assert True

    async def test_get_portal(self, get_session):
        portal = await get_portal(get_session, test_portal_data_model.member_id)
        assert portal.member_id == test_portal_data_model.member_id

    async def test_update_portal(self, get_session):
        portal = await get_portal(get_session, test_portal_data_model.member_id)
        print(portal.refresh_token)
        if portal:
            portal.refresh_token = 'new_refresh_token'
            await refresh_portal(get_session, portal)
            refreshed_portal = await get_portal(get_session, test_portal_data_model.member_id)
            print(refreshed_portal.refresh_token)
            assert refreshed_portal.refresh_token == portal.refresh_token

import pytest
from typing import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.auth import create_jwt
from src.models import PortalModel, UserAuthModel, KtalkSpaceModel, UserModel
from src.db.schemes import Base

from httpx import AsyncClient, ASGITransport
from src.main import app

from environs import Env
from crest.crest import CRestBitrix24

from tests.utils import prepare_tables

from src.logger.custom_logger import logger

env = Env()
env.read_env(path='.env.test', override=True)

"""
Настройки базы данных
"""
TEST_URI = "sqlite+aiosqlite:///data/test.sqlite3"

engine_test = create_async_engine(TEST_URI)
async_session_maker = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False)
# Base.metadata.bind = engine_test

@event.listens_for(engine_test.sync_engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('pragma foreign_keys=ON')
    cursor.close()


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        print("Preparing database...")
        await conn.run_sync(Base.metadata.create_all)
        print("Database is ready")

    async with async_session_maker() as session:
        await prepare_tables(session=session)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


"""
Настройки CRest приложения
"""
client_id = env.str("CLIENT_ID")
client_secret = env.str("CLIENT_SECRET")
webhook = env.str("CLIENT_WEBHOOK")

ktalk_space_name = env.str("KTALK_SPACE_NAME")
ktalk_admin_email = env.str("KTALK_ADMIN_EMAIL")
ktalk_api_key = env.str("KTALK_API_KEY")

crest_auth: CRestBitrix24 = None
crest_webhook: CRestBitrix24 = None

if client_id and client_secret:
    crest_auth = CRestBitrix24(client_id=client_id, client_secret=client_secret)
if webhook:
    crest_webhook = CRestBitrix24(client_webhook=webhook)


refresh_token_admin = env.str("ADMIN_REFRESH_TOKEN")


@pytest.fixture
async def get_portal() -> PortalModel:
    """
    Установи здесь свой refresh_token
    """
    auth = await crest_auth.refresh_token(refresh_token=refresh_token_admin)
    return PortalModel(
        member_id=auth['member_id'],
        client_endpoint=auth['client_endpoint'],
        scope=auth['scope'],
    )


@pytest.fixture
def admin_refresh_token() -> str:
    return refresh_token_admin


@pytest.fixture
async def get_admin_user() -> UserModel:
    auth = await crest_auth.refresh_token(refresh_token=refresh_token_admin)
    return UserModel(
        user_id=auth['user_id'],
        member_id=auth['member_id'],
        is_admin=True,
        name="",
        last_name=""
    )


@pytest.fixture
async def get_jwt_token(get_admin_user: UserModel) -> str:
    return create_jwt(user=get_admin_user)


@pytest.fixture
async def get_admin_auth() -> UserAuthModel:
    auth = await crest_auth.refresh_token(refresh_token=refresh_token_admin)
    return UserAuthModel(
        user_id=auth['user_id'],
        member_id=auth['member_id'],
        client_endpoint=auth['client_endpoint'],
        access_token=auth['access_token'],
        refresh_token=auth['refresh_token']
    )
    

@pytest.fixture
def get_ktalk_space(get_admin_auth: UserAuthModel) -> KtalkSpaceModel:
    if ktalk_space_name and ktalk_admin_email and ktalk_api_key:
        return KtalkSpaceModel(
            member_id=get_admin_auth.member_id,
            space=ktalk_space_name,
            api_key=ktalk_api_key,
            admin_email=ktalk_admin_email
        )
    else:
        logger.error("Для успешного тестирования приложения необходимо добавить ktalk_space_name, ktalk_admin_email и ktalk_api_key в файл .env.test")


"""
Настройки fastapi приложения
"""
async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def add_crest() -> CRestBitrix24:
    if client_id and client_secret:
        app.state.CRest = CRestBitrix24(
            client_id=client_id,
            client_secret=client_secret
        )
    else:
        print("Необходимо задать client_id и client_secret для успешного тестирования")


add_crest()
app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app), base_url="http://localhost") as ac:
        yield ac

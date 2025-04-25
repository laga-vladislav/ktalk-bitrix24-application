from sqlalchemy.ext.asyncio import AsyncSession
from src.db.requests import add_portal, add_ktalk_space, add_user, _add_user_token
from tests.data import DatabaseTestData


async def prepare_tables(session: AsyncSession):
    await add_portal(session, DatabaseTestData.test_portal_data_model)
    print(f"Создан тестовый портал: {DatabaseTestData.test_portal_data_model}")
    await add_ktalk_space(session, DatabaseTestData.test_ktalk_space_data_model_correct)
    print(f"Создано тестовое пространство КТолк: {DatabaseTestData.test_ktalk_space_data_model_correct}")
    await add_user(session, DatabaseTestData.test_user_data_model_correct)
    print(f"Создан тестовый пользователь: {DatabaseTestData.test_user_data_model_correct}")
    await _add_user_token(session, DatabaseTestData.test_user_token_data_model_correct)
    print(f"Создан тестовый токен: {DatabaseTestData.test_user_token_data_model_correct}")

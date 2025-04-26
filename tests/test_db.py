import pytest
from sqlalchemy.exc import IntegrityError

from src.db.requests import add_portal, get_portal, refresh_portal
from src.db.requests import add_ktalk_space, get_ktalk_space, refresh_ktalk_space
from src.db.requests import add_user, get_user, refresh_user
from src.db.requests import set_user_auth, _add_user_auth, get_user_auth, _delete_user_auth, _refresh_user_auth

from tests.data import DatabaseTestData as data
from tests.data import get_random_string


class TestDatabase:
    """
    Portal Section
    """
    async def test_add_portal(self, get_session):
        # Добавим новый уникальный портал для тестирования.
        # портал test_portal_data_model добавляется в _prepare_db,
        # чтобы работали другие методы.
        portal = data.test_portal_data_model.model_copy()
        portal.member_id = get_random_string()

        print(portal)
        await add_portal(get_session, portal)
        assert True


    async def test_get_portal(self, get_session):
        portal = await get_portal(get_session, data.test_portal_data_model.member_id)
        print(portal)
        assert portal.member_id == data.test_portal_data_model.member_id


    async def test_refresh_portal(self, get_session):
        portal = data.test_portal_data_model.model_copy()
        print(portal)

        new_portal = portal.model_copy()
        new_portal.client_endpoint = get_random_string()
        print(new_portal)
        await refresh_portal(get_session, new_portal)

        refreshed_portal = await get_portal(get_session, new_portal.member_id)
        assert refreshed_portal.member_id == new_portal.member_id
        assert refreshed_portal.client_endpoint != portal.client_endpoint


    """
    KTalk Space Section
    """
    async def test_add_ktalk_space_correct(self, get_session):
        # Добавление нового портала необходимо для
        # корректной работы теста на получение портала
        new_portal = data.test_portal_data_model.model_copy()
        new_portal.member_id = get_random_string()
        print(new_portal)
        await add_portal(get_session, new_portal)
        
        ktalk_space = data.test_ktalk_space_data_model_correct.model_copy()
        ktalk_space.member_id = new_portal.member_id
        print(ktalk_space)
        await add_ktalk_space(get_session, ktalk_space)
        assert True

    
    async def test_add_ktalk_space_incorrect(self, get_session):
        ktalk_space = data.test_ktalk_space_data_model_incorrect.model_copy()
        print(ktalk_space)

        with pytest.raises(IntegrityError):
            await add_ktalk_space(get_session, ktalk_space)


    async def test_get_ktalk_space(self, get_session):
        ktalk_space = await get_ktalk_space(get_session, data.test_portal_data_model)
        print(ktalk_space)
        assert ktalk_space.member_id == data.test_ktalk_space_data_model_correct.member_id        


    async def test_refresh_ktalk_space(self, get_session):
        portal = data.test_portal_data_model.model_copy()
        ktalk_space = await get_ktalk_space(get_session, portal)
        print(ktalk_space)
        
        new_ktalk_space = ktalk_space.model_copy()
        new_ktalk_space.space = get_random_string()
        print(new_ktalk_space)
        await refresh_ktalk_space(get_session, new_ktalk_space)

        refreshed_ktalk_space = await get_ktalk_space(get_session, portal)
        assert ktalk_space.space != refreshed_ktalk_space.space


    """
    User Section
    """
    async def test_add_user_correct(self, get_session):
        user = data.test_user_data_model_correct.model_copy()
        print(user)
        await add_user(get_session, user)
        assert True


    async def test_add_user_incorrect(self, get_session):
        user = data.test_user_data_model_incorrect.model_copy()
        print(user)
        with pytest.raises(IntegrityError):
            await add_user(get_session, user)

    async def test_get_user(self, get_session):
        user = data.test_user_data_model_correct.model_copy()
        usr = await get_user(get_session, user.user_id, user.member_id)
        assert user.member_id == usr.member_id

    
    async def test_refresh_user(self, get_session):
        user = data.test_user_data_model_correct.model_copy()
        print(user)

        new_user = user.model_copy()
        new_user.name = get_random_string()
        await refresh_user(get_session, new_user)

        refreshed_user = await get_user(get_session, user.user_id, user.member_id)
        print(refreshed_user)
        assert (user.member_id, user.user_id) == (refreshed_user.member_id, refreshed_user.user_id)
        assert user.name != refreshed_user.name


    """
    User Auth Section
    """
    async def test_add_user_auth_correct(self, get_session):
        user_auth = data.test_user_auth_data_model_correct.model_copy()
        print(user_auth)

        await _delete_user_auth(get_session, user_auth)
        await _add_user_auth(get_session, user_auth)
        assert True

    
    async def test_add_user_token_incorrect(self, get_session):
        user_auth = data.test_user_auth_data_model_incorrect.model_copy()
        print(user_auth)

        # await _delete_user_auth(get_session, user_auth)
        with pytest.raises(IntegrityError):
            await _add_user_auth(get_session, user_auth)


    async def test_get_user_auth(self, get_session):
        user = data.test_user_data_model_correct.model_copy()
        user_auth = data.test_user_auth_data_model_correct.model_copy()
        print(user_auth)
        user_auth_from_db = await get_user_auth(get_session, user)
        print(user_auth_from_db)
        assert (user_auth.access_token,
                user_auth.refresh_token) == (user_auth_from_db.access_token,
                                             user_auth_from_db.refresh_token)
        

    async def test_update_auth(self, get_session):
        user = data.test_user_data_model_correct.model_copy()
        user_auth = data.test_user_auth_data_model_correct.model_copy()
        print(user_auth)

        new_user_auth = user_auth.model_copy()
        new_user_auth.access_token = get_random_string()
        print(new_user_auth)

        await _refresh_user_auth(get_session, new_user_auth)
        refreshed_user_auth = await get_user_auth(get_session, user)
        assert user_auth.access_token != refreshed_user_auth.access_token


    async def test_set_user_auth(self, get_session):
        user = data.test_user_data_model_correct.model_copy()
        user_auth = data.test_user_auth_data_model_correct.model_copy()
        print(user_auth)

        # Добавление
        await _delete_user_auth(get_session, user_auth)
        await set_user_auth(get_session, user_auth)
        assert True

        # Обновление
        new_user_auth = user_auth.model_copy()
        new_user_auth.access_token = get_random_string()
        await set_user_auth(get_session, new_user_auth)
        refreshed_user_auth = await get_user_auth(get_session, user)
        print(refreshed_user_auth)

        assert user_auth.access_token != refreshed_user_auth.access_token

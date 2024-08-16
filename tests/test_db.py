from src.db.models import PortalModel
from src.db.requests import add_portal, get_portal, refresh_portal
from tests.conftest import get_random_string


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

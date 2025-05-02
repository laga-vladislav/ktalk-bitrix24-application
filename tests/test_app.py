from httpx import AsyncClient
from src.models import UserModel, UserAuthModel, KtalkSpaceModel

from src.bitrix_requests import get_admin_status, get_user_info
from src.bitrix_requests import create_ktalk_company_calendar, get_ktalk_company_calendar
from src.bitrix_requests import create_ktalk_calendar_event, get_calendar_event
from src.bitrix_requests import send_notification_to_blogpost
from src.bitrix_requests import create_robot_request, _get_base_domain_from_client_endpoint, add_todo_activity

from tests.conftest import crest_auth
from crest.models import CallRequest, AuthTokens
from src.models import BitrixCalendarModel

from tests.data import KTalkTestData as data
from tests.data import DatabaseTestData as db_data


class TestBitrixApplication:

    async def test_refresh_token(self, admin_refresh_token: str):
        result = await crest_auth.refresh_token(admin_refresh_token)
        print(result)
        assert isinstance(result, dict) and 'access_token' in result.keys()


    async def test_get_admin_status(self, get_admin_auth: UserAuthModel):
        auth_tokens = AuthTokens(**get_admin_auth.model_dump())
        result = await get_admin_status(
            CRest=crest_auth,
            tokens=auth_tokens,
            client_endpoint=get_admin_auth.client_endpoint
        )
        print(result)
        assert isinstance(result, bool)


    async def test_get_user_info(self, get_admin_auth: UserAuthModel):
        auth_tokens = AuthTokens(**get_admin_auth.model_dump())
        result = await get_user_info(
            CRest=crest_auth,
            tokens=auth_tokens,
            client_endpoint=get_admin_auth.client_endpoint,
            member_id=get_admin_auth.member_id
        )
        print(result)
        assert isinstance(result, UserModel)


    async def test_create_company_calendar(self, get_admin_auth: UserAuthModel):
        company_calendar_id: int = await create_ktalk_company_calendar(
            crest=crest_auth,
            user_auth=get_admin_auth,
            calendar_name=data.calendar_name
        )
        print(company_calendar_id)
        assert isinstance(company_calendar_id, int)
        data.calendar_id = company_calendar_id
        data.save()


    async def test_get_company_calendar(self, get_admin_auth: UserAuthModel):
        """
        Условия:
        1. Необходим созданный календарь (test_create_company_calendar)
        """
        company_calendar: BitrixCalendarModel = await get_ktalk_company_calendar(
            crest=crest_auth,
            user_auth=get_admin_auth,
            calendar_name=data.calendar_name,
            calendar_id=data.calendar_id
        )
        print(company_calendar)
        assert isinstance(company_calendar, BitrixCalendarModel)


    async def test_create_ktalk_calendar_event(
        self,
        get_admin_auth: UserAuthModel
    ):
        """
        Условия:
        1. Необходим созданный календарь (test_create_company_calendar)
        """
        company_calendar: BitrixCalendarModel = await get_ktalk_company_calendar(
            crest=crest_auth,
            user_auth=get_admin_auth,
            calendar_name=data.calendar_name,
            calendar_id=data.calendar_id
        )
        
        event_id_in_calendar: int = await create_ktalk_calendar_event(
            crest=crest_auth,
            calendar_id=company_calendar.id,
            meeting=data.meeting_model,
            created_meeting_information=data.meeting_information_back_answer,
            user_auth=get_admin_auth
        )
        print(event_id_in_calendar)
        assert isinstance(event_id_in_calendar, int)
        data.meeting_id = event_id_in_calendar
        data.save()


    async def test_get_calendar_event(self, get_admin_auth: UserAuthModel):
        """
        Условия:
        1. Необходим созданный календарь (test_create_company_calendar)
        2. Необходимо созданное событие в календаре (test_create_ktalk_calendar_event)
        """
        calendar: BitrixCalendarModel = await get_ktalk_company_calendar(
            crest=crest_auth,
            user_auth=get_admin_auth,
            calendar_name=data.calendar_name,
            calendar_id=data.calendar_id
        )
        print(calendar)
        calendar_event: dict = await get_calendar_event(
            crest=crest_auth,
            calendar_id=calendar.id,
            calendar_event_id=data.meeting_id,
            user_auth=get_admin_auth
        )
        print(calendar_event)
        assert(isinstance(calendar_event, dict))


    async def test_send_notification_to_blogpost(self, get_admin_auth: UserAuthModel):
        result = await send_notification_to_blogpost(
            crest=crest_auth,
            meeting=data.meeting_model,
            created_meeting_information=data.meeting_information_back_answer,
            user_auth=get_admin_auth
        )
        print(result)
        assert isinstance(result['result'], int)


    async def test_create_robot_request(self, get_admin_auth: UserAuthModel):
        result = await create_robot_request(
            CRest=crest_auth,
            user_auth=get_admin_auth,
            application_domain=_get_base_domain_from_client_endpoint(get_admin_auth.client_endpoint)
        )
        print(result)
        assert isinstance(result, bool) or isinstance(result, dict) and result['error'] == 'ERROR_ACTIVITY_ALREADY_INSTALLED'


    async def test_add_company(self, get_admin_auth: UserAuthModel):
        result = await crest_auth.call(
            CallRequest(
                method="crm.company.add",
                params={
                    "TITLE": "ООО Рудник",
                    "PHONE": [
                        {
                            "VALUE": "88005553535",
                            "VALUE_TYPE": "WORK"
                        }
                    ]
                }
            ),
            client_endpoint=get_admin_auth.client_endpoint,
            auth_tokens=AuthTokens(
                **get_admin_auth.model_dump()
            )
        )
        print(result)
        assert isinstance(result['result'], int)
        data.company_id = result['result']
        data.save()


    async def test_add_contact(self, get_admin_auth: UserAuthModel):
        result = await crest_auth.call(
            CallRequest(
                method="crm.contact.add",
                params={
                    "NAME": "Рудничок Евгеньевич",
                    "PHONE": [
                        {
                            "VALUE": "88005553535",
                            "VALUE_TYPE": "WORK"
                        }
                    ]
                }
            ),
            client_endpoint=get_admin_auth.client_endpoint,
            auth_tokens=AuthTokens(
                **get_admin_auth.model_dump()
            )
        )
        print(result)
        assert isinstance(result['result'], int)
        data.contact_id = result['result']
        data.save()


    async def test_add_deal(self, get_admin_auth: UserAuthModel):
        """
        Условия:
        1. Созданная компания (test_add_company)
        2. Созданный контакт (test_add_contact)
        """
        result = await crest_auth.call(
            CallRequest(
                method="crm.deal.add",
                params={
                    "TITLE": "ЗДЕЛКА ВЕКА!!!!!",
                    "COMPANY_ID": data.company_id,
                    "CONTACTS_IDS": [data.contact_id]
                }
            ),
            client_endpoint=get_admin_auth.client_endpoint,
            auth_tokens=AuthTokens(
                **get_admin_auth.model_dump()
            )
        )
        print(result)
        assert isinstance(result['result'], int)
        data.deal_id = result['result']
        data.save()


    async def test_add_todo_activity(self, get_admin_auth: UserAuthModel):
        """
        Условия:
        1. Необходима созданная сделка (test_add_deal)
        """
        result = await add_todo_activity(
            crest=crest_auth,
            user_auth=get_admin_auth,
            creator_id=get_admin_auth.user_id,
            owner_id=data.deal_id,
            meeting=data.meeting_model,
            meeting_url=data.meeting_information_back_answer.url
        )
        print(result)
        assert isinstance(result['result'], dict)


class TestFastapiApplication:
    async def test_endpoint_install(self, ac: AsyncClient, get_admin_auth: UserAuthModel):
        result = await ac.post(
            '/install',
            data={
                "REFRESH_ID": get_admin_auth.refresh_token
            }
        )
        print(result)


    async def test_endpoint_set_settings(self, ac: AsyncClient, get_ktalk_space: KtalkSpaceModel):
        result = await ac.post(
            '/set-settings',
            json=get_ktalk_space.model_dump()
        )
        print(result)

    
    async def test_endpoint_create_internal_meeting(self, ac: AsyncClient, get_admin_auth: UserAuthModel, get_ktalk_space: KtalkSpaceModel):
        # result = await ac.post(
        #     '/create-internal-meeting',

        # )
        ...
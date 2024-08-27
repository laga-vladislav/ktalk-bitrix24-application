from httpx import AsyncClient
from src.models import PortalModel
from src.router.create_meeting import add_todo_activity
from tests.conftest import crest_webhook, crest_auth
from crest.models import CallRequest, AuthTokens
from src.ktalk.models import MeetingModel, ParticipantsModel, SelectedClientsModel


async def test_refresh_token(get_portal: PortalModel):
    result = await crest_auth.refresh_token(get_portal.refresh_token)
    print(result)


async def test_add_robot_auth(get_portal: PortalModel):
    result = await crest_auth.call(
        CallRequest(
            method="bizproc.robot.add",
            params={
                'CODE': 'robot',
                'HANDLER': 'https://firstly-climbing-goat.ngrok-free.app/robot',
                'AUTH_USER_ID': 1,
                'NAME': 'Robot',
                'PROPERTIES': {
                    'bool': {
                        'Name': 'Да/Нет',
                        'Type': 'bool',
                        'Required': 'Y',
                        'Multiple': 'N'
                    },
                    'date': {
                        'Name': 'Дата',
                        'Type': 'date'
                    },
                    'datetime': {
                        'Name': 'Дата/Время',
                        'Type': 'datetime'
                    },
                    'double': {
                        'Name': 'Число',
                        'Type': 'double',
                        'Required': 'Y'
                    },
                    'int': {
                        'Name': 'Целое число',
                        'Type': 'int'
                    },
                    'select': {
                        'Name': 'Список',
                        'Type': 'select',
                        'Options': {
                            'one': 'one',
                                'two': 'two'
                        }
                    },
                    'string': {
                        'Name': 'Строка',
                        'Type': 'string',
                        'Default': 'default string value'
                    },
                    'text': {
                        'Name': 'Текст',
                        'Type': 'text'
                    },
                    'user': {
                        'Name': 'Пользователь',
                        'Type': 'user'
                    }
                }
            }
        ),
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result)


async def test_add_activity_todo(get_portal: PortalModel):
    body = {
        "subject": "Созвон. По будням, в 20:00, только на СТС",
        "description": "Пожалуйста, не подключайтесь!",
        "start": "2024-08-28T03:20:00.000Z",
        "end": "2024-08-28T04:21:00.000Z",
        "timezone": "GMT+9",
        "allowAnonymous": True,
        "enableSip": True,
        "pinCode": "1234",
        "enableAutoRecording": True,
        "isRecurring": False
    }
    meeting = MeetingModel(**body)
    deal = await test_get_last_deal(get_portal)
    print(deal)

    result = await add_todo_activity(
        crest=crest_auth,
        portal=get_portal,
        creator_id=1,
        owner_id=deal.get('ID'),
        meeting=meeting,
        meeting_url="example.com",
        participants=ParticipantsModel(
            colleguesId=[1, 10],
            selectedClients=[
                SelectedClientsModel(
                    entityId=deal['COMPANY_ID'], entityTypeId=4),
                SelectedClientsModel(
                    entityId=deal['CONTACT_ID'], entityTypeId=3)
            ]
        )
    )
    print(result)
    assert isinstance(result, dict)


async def test_get_contacts_from_deal(get_portal: PortalModel):
    """
    36465
    """
    result = await crest_auth.call(
        CallRequest(
            method="crm.deal.contact.items.get",
            params={
                'id': 1
            }
        ),
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result)


async def test_get_last_deal(get_portal: PortalModel):
    result = await crest_auth.call(
        CallRequest(
            method="crm.deal.list",
            params={
                'order': {
                    'ID': 'DESC'
                },
                'select': [
                    'ID', 'COMPANY_ID', 'CONTACT_ID'
                ]
            }
        ),
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result.get('result')[0])
    assert result
    return result.get('result')[0]


async def test_contact_add_method_webhook():
    call_request = CallRequest(method="crm.contact.add", params={
                               "fields": {'name': 'pytest'}})
    for i in range(1):
        result = await crest_webhook.call(request=call_request)
        print(f"Method: '{call_request.method}'. Attempt # {
              i}. Result: {result}\n")


async def test_contact_add_method_auth_batch(get_portal: PortalModel):
    call_requests = [
        CallRequest(
            method="crm.contact.add",
            params={
                "fields": {'name': 'pytest_batch'}
            }
        )
        for i in range(60)
    ]

    result = await crest_auth.call_batch(
        request_batch=call_requests,
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token),
    )
    print(result)
    assert isinstance(result, list)


async def test_endpoint_create_meeting(get_portal: PortalModel, ac: AsyncClient):
    auth = await crest_auth.refresh_token(refresh_token=get_portal.refresh_token)
    tokens = AuthTokens(**auth)
    meeting = MeetingModel(**{
        "subject": "Созвон. По будням, в 20:00, только на СТС",
        "description": "Пожалуйста, не подключайтесь!",
        "start": "2024-08-28T03:20:00.000Z",
        "end": "2024-08-28T04:21:00.000Z",
        "timezone": "GMT+9",
        "allowAnonymous": True,
        "enableSip": True,
        "pinCode": "56636",
        "enableAutoRecording": True,
        "isRecurring": False
    })
    participants = ParticipantsModel(
        colleguesId=[1, 10],
        selectedClients=[
            SelectedClientsModel(
                entityId=2, entityTypeId=4),
            SelectedClientsModel(
                entityId=36469, entityTypeId=3)
        ]
    )
    result = await ac.post(
        '/create_meeting',
        json={
            "tokens": tokens.model_dump(),
            "meeting": meeting.model_dump(),
            "participants": participants.model_dump(exclude_none=True)
        },
        params={
            "creatorId": 1,
            "ownerId": 320
        }
    )
    print(result)
    assert result.status_code == 200

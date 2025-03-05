from httpx import AsyncClient
from src.models import PortalModel
from src.router.create_external_meeting import add_todo_activity
from tests.conftest import crest_webhook, crest_auth
from crest.models import CallRequest, AuthTokens
from src.models import ParticipantsModel, SelectedClientsModel
from src.ktalk.models import MeetingModel, KTalkBackAnswerModel

body = {
    "subject": "Созвон. По будням, в 20:00, только на СТС",
    "description": "Пожалуйста, не подключайтесь!",
    "start": 1741186653000,
    "end": 1741197412000,
    "timezone": "GMT+9",
    "allowAnonymous": True,
    "enableSip": True,
    "enableAutoRecording": True
}
meeting = MeetingModel(**body)
meeting_information = KTalkBackAnswerModel(
    url='example.com'
)


async def test_refresh_token(get_portal: PortalModel):
    result = await crest_auth.refresh_token(get_portal.refresh_token)
    print(result)


async def test_add_robot_auth(get_portal: PortalModel):
    result = await crest_auth.call(
        CallRequest(
            method="bizproc.robot.add",
            params={
                'CODE': 'robotd',
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


async def test_get_activities_todo(get_portal: PortalModel):
    call = CallRequest(
        method='crm.activity.list',
        params={
            'filter':
            {
                "OWNER_TYPE_ID": 2,
                "OWNER_ID": 2
            }
        }
    )
    result = await crest_auth.call(
        call,
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result)


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


async def test_endpoint_create_meeting(ac: AsyncClient):
    meeting = MeetingModel(**body)
    print(meeting)
    participants = ParticipantsModel(
        colleguesId=[1, 8],
        selectedClients=[
            SelectedClientsModel(
                entityId=2, entityTypeId=4),
            SelectedClientsModel(
                entityId=2, entityTypeId=3)
        ]
    )
    result = await ac.post(
        '/create_meeting',
        json={
            "meeting": meeting.model_dump(),
            "participants": participants.model_dump(exclude_none=True)
        },
        params={
            "creatorId": 1,
            "ownerId": 2,
            "memberId": "43c4e7d9d8651368fb77cd2821e99926"
        }
    )
    print(result.json())
    assert result.status_code == 200


async def test_get_public_chat(get_portal: PortalModel):
    call = CallRequest(
        method="im.recent.list"
    )
    result = await crest_auth.call(
        request=call,
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    # print(result['result']['items'])
    public_chat = next(
        (c for c in result['result']['items'] if c['title'] == 'Общий чат'), None)
    print(public_chat)
    assert isinstance(public_chat['id'],
                      str) and public_chat['title'] == 'Общий чат'
    return public_chat


async def test_send_meeting_to_chat_batch(
    get_portal: PortalModel,
    chat_id: str = 'chat2',
    meeting: MeetingModel = meeting,
    meeting_information: KTalkBackAnswerModel = meeting_information
):
    call_batches = []
    call_batches.append(
        CallRequest(
            method='im.message.add',
            params={
                'DIALOG_ID': chat_id,
                'MESSAGE': '[B]Создана видеовстреча[/B]',
                'SYSTEM': 'Y',
            }
        )
    )

    message_text = f"""[B]Тема:[/B] {meeting.subject}
[B]Описание:[/B] {meeting.description}
[B]Подключение: [URL={meeting_information.url}]по ссылке[/URL][/B]
[B]Пин-код:[/B] {meeting.pinCode}

[I]Создано [URL=example.com]событие[/URL] в календаре компании[/I]"""
    call_batches.append(
        CallRequest(
            method='im.message.add',
            params={
                'DIALOG_ID': chat_id,
                'MESSAGE': message_text
            }
        )
    )

    result = await crest_auth.call_batch(
        call_batches,
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result)


async def test_create_meeting_in_calendar(get_portal: PortalModel, calendar_id: int = 3, meeting: MeetingModel = meeting):
    print(meeting.start_ktalk)
    print(meeting.end_ktalk)
    call = CallRequest(
        method='calendar.event.add',
        params={
            'type': 'company_calendar',
            'ownerId': 0,
            'from': meeting.start_ktalk,
            'to': meeting.end_ktalk,
            'section': calendar_id,
            'name': meeting.subject,
            'description': meeting.description
        }
    )
    result = await crest_auth.call(
        request=call,
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result)


async def test_send_title_message_to_chat(get_portal: PortalModel, chat_id: str = 'chat2'):
    call = CallRequest(
        method='im.message.add',
        params={
            'DIALOG_ID': chat_id,
            'MESSAGE': '[B]Создана видеовстреча[/B]',
            'SYSTEM': 'Y',
        }
    )
    result = await crest_auth.call(
        request=call,
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result)
    assert isinstance(result['result'], int)
    return result['result']


async def test_send_information_message_to_chat(
        get_portal: PortalModel,
        meeting: MeetingModel = meeting,
        meeting_information: KTalkBackAnswerModel = meeting_information,
        chat_id: str = 'chat2'
) -> int:
    message_text = f"""[B]Тема:[/B] {meeting.subject}
[B]Описание:[/B] {meeting.description}
[B]Подключение: [URL={meeting_information.url}]по ссылке[/URL][/B]
[B]Пин-код:[/B] {meeting.pinCode}

[I]Создано [URL=example.com]событие[/URL] в календаре компании[/I]"""
    call = CallRequest(
        method='im.message.add',
        params={
            'DIALOG_ID': chat_id,
            'MESSAGE': message_text
        }
    )
    result = await crest_auth.call(
        request=call,
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result)
    return result['result']


async def test_get_calendar(get_portal: PortalModel, calendar_name: str = 'Календарь встреч КТолк'):
    call = CallRequest(
        method="calendar.section.get",
        params={
            "type": "company_calendar",
            "ownerId": 0
        }
    )
    result = await crest_auth.call(
        request=call,
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )

    # if not (any(calendar['NAME'] == calendar_name for calendar in result['result'])):
    #     await test_add_company_calendar(get_portal=get_portal, calendar_name=calendar_name)

    # result = await crest_auth.call(
    #     request=call,
    #     client_endpoint=get_portal.client_endpoint,
    #     auth_tokens=AuthTokens(
    #         access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    # )
    # print(result['result'])
    ktalk_calendar = next(
        (calendar for calendar in result['result'] if calendar['NAME'] == calendar_name), None)
    print(ktalk_calendar)

    assert ktalk_calendar['NAME'] == calendar_name

    return ktalk_calendar


async def test_add_company_calendar(get_portal: PortalModel, calendar_name: str = 'Календарь встреч КТолк') -> int:
    """
    Делать при установке
    """
    call = CallRequest(
        method="calendar.section.add",
        params={
            "type": "company_calendar",
            "ownerId": 0,
            "name": calendar_name,
            "description": "В данном календаре находятся встречи, созданные сотрудниками вашей организации, а также встречи с клиентами"
        }
    )
    result = await crest_auth.call(
        request=call,
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result)
    assert isinstance(result['result'], int)
    return result['result']


async def test_add_calendar(get_portal: PortalModel, calendar_name: str = 'Календарь встреч КТолк'):
    """
    Не буду использовать
    """
    call = CallRequest(
        method="calendar.section.add",
        params={
            "type": "user",
            "ownerId": 1,  # изменяемыый
            "name": calendar_name,
            "description": "В данном календаре находятся внутренние встречи, созданные сотрудниками вашей организации"
        }
    )
    result = await crest_auth.call(
        request=call,
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result)
    assert isinstance(result['result'], int)

    return result['result']


async def test_calendar(get_portal: PortalModel):
    call = CallRequest(
        method="calendar.section.get",
        params={
            'type': 'user',
            'ownerId': 1
        }
    )  # 4
    call2 = CallRequest(
        method="im.recent.list"
    )  # 2
    call3 = CallRequest(
        method='calendar.event.add',
        params={
            "type": "company_calendar",
            "ownerId": 0,
            "name": "Встреча в общем чате",
            "from": "2025-02-28T10:00:00+03:00",
            "to": "2025-02-28T11:00:00+03:00",
            "section": 4,
            # "attendees": [1, 2, 3]
        }
    )
    call4 = CallRequest(
        method='im.message.add',
        params={
            'DIALOG_ID': "chat2",
            'MESSAGE': 'Создана встреча-ча-ча',
            'SYSTEM': 'Y'
        }
    )  # 40
    call5 = CallRequest(
        method='im.message.share',
        params={
            'MESSAGE_ID': 40,
            'DIALOG_ID': 'chat2',
            'TYPE': 'CALEND'
        }
    )
    call6 = CallRequest(
        method='calendar.event.get',
        params={
            'type': 'company_calendar',
            'ownerId': "",
            'section': [3],
        }
    )
    call7 = CallRequest(
        method="calendar.section.get",
        params={
            "type": "company_calendar",
            "ownerId": 0
        }
    )
    result = await crest_auth.call(
        call7,
        client_endpoint=get_portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    from src.models import BitrixCalendarModel
    for meeting in result['result']:
        if meeting['NAME'] == 'Календарь встреч КТолк':
            print(BitrixCalendarModel(**meeting))
    # for item in result['result']['items']:
    #     if item['title'] == 'Общий чат':
    #         print(item)

from crest.models import AuthTokens, CallRequest
from src.models import PortalModel, UserModel
from src.ktalk.models import MeetingModel
from crest.crest import CRestBitrix24
from src.models import ParticipantsModel, AppOptionModel, BitrixAppStorageModel, BitrixCalendarModel
from src.ktalk.models import MeetingModel, KTalkBackAnswerModel

from src.logger.custom_logger import logger

CALENDAR_NAME = 'Календарь встреч КТолк'
CALENDAR_ID = int
CALENDAR_EVENT_ID = int
CHAT_ID = str  # Строка! формата chatXXX. Общий чат вроде всегда chat2


class MessageText:
    TEMPLATE = """[B]Тема:[/B] {subject}
[B]Описание:[/B] {description}
[B]Подключение: [URL={url}]по ссылке[/URL][/B]
[B]Пин-код:[/B] {pin_code}
[I]Создано событие в [URL={calendar_url}]календаре компании[/URL][/I]"""

    @classmethod
    def format(cls, subject, description, meeting_url, pin_code, calendar_url):
        return cls.TEMPLATE.format(
            subject=subject,
            description=description,
            url=meeting_url,
            pin_code=pin_code,
            calendar_url=calendar_url
        )


async def set_option_call(
    crest_instance: CRestBitrix24,
    portal: PortalModel,
    option_name: str,
    option_data: str
):
    endpoint = portal.client_endpoint
    tokens = AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    response = await crest_instance.call(
        CallRequest(
            method="app.option.set",
            params={
                'options': {
                    option_name: option_data
                }
            }
        ),
        client_endpoint=endpoint,
        auth_tokens=tokens
    )
    return response


async def set_options_call(
    crest_instance: CRestBitrix24,
    portal: PortalModel,
    options: list[AppOptionModel]
):
    endpoint = portal.client_endpoint
    tokens = AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    params = {
        'options': {}
    }
    for option in options:
        params['options'][option.option_name] = option.option_data

    request = CallRequest(
        method="app.option.set",
        params=params
    )

    response = await crest_instance.call(
        request,
        client_endpoint=endpoint,
        auth_tokens=tokens
    )
    return response


async def get_option_value_by_name(
    crest_instance: CRestBitrix24,
    portal: PortalModel,
    option_name: str
) -> str:
    endpoint = portal.client_endpoint
    tokens = AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    response = await crest_instance.call(
        CallRequest(
            method="app.option.get",
            params={
                'option': option_name
            }
        ),
        client_endpoint=endpoint,
        auth_tokens=tokens
    )
    return response.get('result') if response.get('result') else ''


async def get_all_options_dict(
    crest_instance: CRestBitrix24,
    portal: PortalModel
) -> dict:
    endpoint = portal.client_endpoint
    tokens = AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    response = await crest_instance.call(
        CallRequest(
            method="app.option.get"
        ),
        client_endpoint=endpoint,
        auth_tokens=tokens
    )
    return dict(response.get('result')) if response.get('result') else {}


async def get_all_options_bitrix_options(
    crest_instance: CRestBitrix24,
    portal: PortalModel
) -> BitrixAppStorageModel | None:
    options = await get_all_options_dict(
        crest_instance=crest_instance,
        portal=portal
    )
    return BitrixAppStorageModel(**dict(options)) if options else None


async def create_ktalk_company_calendar(
    crest: CRestBitrix24,
    portal: PortalModel,
    calendar_name: str = CALENDAR_NAME,
    user: UserModel = None
) -> CALENDAR_ID:
    """
    Создать календарь компании, общий для всех сотрудников.
    """
    tokens = AuthTokens(
        access_token=user.access_token,
        refresh_token=user.refresh_token
    ) if user else AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    call = CallRequest(
        method="calendar.section.add",
        params={
            "type": "company_calendar",
            "ownerId": 0,
            "name": calendar_name,
            "description": "В данном календаре находятся встречи, созданные сотрудниками вашей организации, а также встречи с клиентами"
        }
    )
    result = await crest.call(
        request=call,
        client_endpoint=portal.client_endpoint,
        auth_tokens=tokens
    )
    return result['result']


async def get_ktalk_company_calendar(
    crest: CRestBitrix24,
    portal: PortalModel,
    user: UserModel = None,
    calendar_name: str = CALENDAR_NAME,
    calendar_id: CALENDAR_ID = None
) -> BitrixCalendarModel | None:
    tokens = AuthTokens(
        access_token=user.access_token,
        refresh_token=user.refresh_token
    ) if user else AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    call = CallRequest(
        method="calendar.section.get",
        params={
            "type": "company_calendar",
            "ownerId": 0
        }
    )
    result = await crest.call(
        request=call,
        client_endpoint=portal.client_endpoint,
        auth_tokens=tokens)

    if not calendar_id and not calendar_name:
        logger.error(
            "Ошибка. Чтобы получить календарь, необходимо передать calendar_name и/или calendar_id")
        return None

    for meeting in result['result']:
        if calendar_id and calendar_name:
            if meeting['ID'] == str(calendar_id) and meeting['NAME'] == calendar_name:
                return BitrixCalendarModel(**meeting)
        elif calendar_id:
            if meeting['ID'] == str(calendar_id):
                return BitrixCalendarModel(**meeting)
        elif calendar_name:
            if meeting['NAME'] == calendar_name:
                return BitrixCalendarModel(**meeting)

    return None


async def create_ktalk_calendar_event(
    crest: CRestBitrix24,
    calendar_id: CALENDAR_ID,
    meeting: MeetingModel,
    created_meeting_information: KTalkBackAnswerModel,
    portal: PortalModel,
    user: UserModel = None,
) -> CALENDAR_EVENT_ID:
    description = f"{meeting.description}\n\nСсылка на встречу: {created_meeting_information.url}\nПин-код: {meeting.pinCode}".lstrip()

    tokens = AuthTokens(
        access_token=user.access_token,
        refresh_token=user.refresh_token
    ) if user else AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    call = CallRequest(
        method='calendar.event.add',
        params={
            'type': 'company_calendar',
            'ownerId': 0,
            'from_ts': meeting.start_ktalk,
            'to_ts': meeting.start_ktalk,
            'section': calendar_id,
            'name': meeting.subject,
            'description': description
        }
    )
    result = await crest.call(
        request=call,
        client_endpoint=portal.client_endpoint,
        auth_tokens=tokens
    )
    return result


async def get_calendar_event(
    crest: CRestBitrix24,
    calendar_id: CALENDAR_ID,
    calendar_event_id: CALENDAR_EVENT_ID,
    portal: PortalModel,
    user: UserModel = None
) -> dict | None:
    tokens = AuthTokens(
        access_token=user.access_token,
        refresh_token=user.refresh_token
    ) if user else AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    call = CallRequest(
        method='calendar.event.get',
        params={
            'type': 'company_calendar',
            'ownerId': "",
            'section': [calendar_id],
        }
    )
    result = crest.call(
        request=call,
        client_endpoint=portal.client_endpoint,
        auth_tokens=tokens
    )
    for meeting in result['result']:
        if meeting['ID'] == str(calendar_event_id):
            return (meeting)
    return None


async def get_public_chat(
    crest: CRestBitrix24,
    portal: PortalModel,
    user: UserModel = None
) -> CHAT_ID | None:
    tokens = AuthTokens(
        access_token=user.access_token,
        refresh_token=user.refresh_token
    ) if user else AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    call = CallRequest(
        method="im.recent.list"
    )
    result = await crest.call(
        request=call,
        client_endpoint=portal.client_endpoint,
        auth_tokens=tokens
    )

    public_chat = next(
        (c for c in result['result']['items'] if c['title'] == 'Общий чат'), None)

    return public_chat['id'] if public_chat else None


async def send_notification_message_to_chat(
    crest: CRestBitrix24,
    chat_id: CHAT_ID,
    meeting: MeetingModel,
    created_meeting_information: KTalkBackAnswerModel,
    # ktalk_calendar: BitrixCalendarModel,
    portal: PortalModel,
    user: UserModel = None
) -> None:
    tokens = AuthTokens(
        access_token=user.access_token,
        refresh_token=user.refresh_token
    ) if user else AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    base_domain = _get_base_domain_from_client_endpoint(portal.client_endpoint)

    logger.debug(created_meeting_information.url)

    message_text = MessageText.format(
        subject=meeting.subject,
        description=meeting.description,
        meeting_url=created_meeting_information.url,
        pin_code=meeting.pinCode,
        calendar_url=base_domain + '/calendar'
    )

    call_batches = [
        CallRequest(
            method='im.message.add',
            params={
                'DIALOG_ID': chat_id,
                'MESSAGE': '[B]Создана видеовстреча[/B]',
                'SYSTEM': 'Y',
            }
        ),
        CallRequest(
            method='im.message.add',
            params={
                'DIALOG_ID': chat_id,
                'MESSAGE': message_text
            }
        )
    ]

    await crest.call_batch(
        call_batches,
        client_endpoint=portal.client_endpoint,
        auth_tokens=tokens
    )


def _get_base_domain_from_client_endpoint(cliend_endpoint: str) -> str:
    return cliend_endpoint.split("/rest/")[0]


async def create_robot_request(
    CRest: CRestBitrix24,
    portal: PortalModel,
    application_domain: str
):
    return await CRest.call(
        CallRequest(
            method="bizproc.robot.add",
            params={
                'CODE': 'ktalk_robot',
                'HANDLER': f'{application_domain}/ktalk_robot',
                'AUTH_USER_ID': 1,
                'NAME': 'Робот КТолк',
                "PROPERTIES": {
                    "subject": {
                        "name": "Тема встречи",
                        "type": "string",
                        "required": "Y"
                    },
                    "description": {
                        "name": "Текст приглашения",
                        "type": "string",
                        "required": "Y"
                    },
                    "start": {
                        "name": "Дата и время начала",
                        "type": "datetime",
                        "required": "Y"
                    },
                    "end": {
                        "name": "Дата и время окончания",
                        "type": "datetime",
                        "required": "Y"
                    },
                    "timezone": {
                        "name": "Часовой пояс",
                        "type": "string",
                        "required": "Y"
                    },
                    "allowAnonymous": {
                        "name": "Подключение внешних пользователей",
                        "type": "bool",
                        "required": "Y"
                    },
                    "enableSip": {
                        "name": "Подключение по звонку",
                        "type": "bool",
                        "required": "Y"
                    },
                    "enableAutoRecording": {
                        "name": "Автоматическая запись встречи",
                        "type": "bool",
                        "required": "Y"
                    },
                    "pinCode": {
                        "name": "Pin-код (от 4 до 6 цифр)",
                        "type": "int",
                        "required": "N"
                    }
                }
            }
        ),
        client_endpoint=portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=portal.access_token,
            refresh_token=portal.refresh_token
        )
    )


async def add_todo_activity(
    crest: CRestBitrix24,
    portal: PortalModel,
    creator_id: int,
    owner_id: int,
    meeting: MeetingModel,
    meeting_url: str,
    participants: ParticipantsModel = None,
    owner_type_id: int = 2
):
    """
    Создать дело внутри объекта CRM.
    owner_id - id объекта CRM. Например, id сделки.
    owner_type_id - тип объекта CRM. Например, 2 - это сделка.
    """
    # selected_clients_dicts = [client.model_dump()
    #                           for client in participants.selectedClients]
    # meeting_str_date = MeetingKTalkFormatDateModel(**dict(meeting))
    call_request = CallRequest(
        method="crm.activity.todo.add",
        params={
            'ownerTypeId': owner_type_id,
            'ownerId': owner_id,
            'title': meeting.subject,
            'description': meeting.description,
            'deadline': meeting.end_todo_activity,
            'responsibleId': creator_id,
            'settings': [
                {
                    'link': meeting_url,
                    'id': 'link'
                },
                {
                    'from': meeting.start_ktalk,
                    'to': meeting.end_ktalk,
                    'duration': 1200000,
                    'location': '',
                    # 'selectedUserIds': participants.colleguesId,
                    'id': 'calendar'
                },
                {
                    # 'selectedClients': selected_clients_dicts,
                    'id': 'client'
                }
            ],
            "colorId": 5,
            "pingOffsets": [0, 15, 60, 1440]
        }
    )
    endpoint = portal.client_endpoint
    tokens = AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )
    response = await crest.call(
        request=call_request,
        client_endpoint=endpoint,
        auth_tokens=tokens
    )
    return response

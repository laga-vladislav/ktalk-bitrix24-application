from crest.models import AuthTokens, CallRequest
from src.models import UserModel, UserAuthModel
from src.ktalk.models import MeetingModel
from crest.crest import CRestBitrix24
from src.models import ParticipantsModel, BitrixCalendarModel
from src.ktalk.models import MeetingModel, KTalkBackAnswerModel
from src.utils import get_offset_sec

from src.logger.custom_logger import logger

CALENDAR_NAME = 'Календарь встреч КТолк'
CALENDAR_ID = int
CALENDAR_EVENT_ID = int
CHAT_ID = str  # Строка! формата chatXXX. Общий чат вроде всегда chat2


class MessageText:
    TEMPLATE = """[B]Описание:[/B] {description}
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


async def get_user_info(CRest: CRestBitrix24, tokens: AuthTokens, client_endpoint: str, member_id: str) -> UserModel:
    user_info: dict = await get_user_raw_info(
        CRest=CRest, tokens=tokens, client_endpoint=client_endpoint, member_id=member_id
    )
    is_admin = await get_admin_status(CRest, tokens, client_endpoint)
    return UserModel(
        member_id=member_id,
        user_id=int(user_info['ID']),
        name=user_info['NAME'],
        last_name=user_info['LAST_NAME'],
        is_admin=bool(is_admin)
    )


async def get_user_raw_info(CRest: CRestBitrix24, tokens: AuthTokens, client_endpoint: str, member_id: str) -> dict:
    """
    Возвращает полную информацию о пользователе.
     Returns:
        dict: Словарь с данными пользователя. Пример структуры

            {
                'ID': '1',
                'XML_ID': '62328606',
                'ACTIVE': True,
                'NAME': 'Name',
                'LAST_NAME': 'LastName',
                'EMAIL': 'syjuneci@asciibinder.net',
                'LAST_LOGIN': '2025-05-07T14:53:09+03:00',
                'DATE_REGISTER': '2025-04-18T03:00:00+03:00',
                'IS_ONLINE': 'Y',
                'TIME_ZONE_OFFSET': '21600',
                'TIMESTAMP_X': '21.04.2025 06:45:49',
                'LAST_ACTIVITY_DATE': '2025-05-07 18:04:17',
                'PERSONAL_GENDER': '',
                'PERSONAL_BIRTHDAY': '',
                'UF_EMPLOYMENT_DATE': '',
                'UF_DEPARTMENT': [1]
            }
    """
    inforeq = CallRequest(method="user.current")
    user_info = await CRest.call(
        request=inforeq,
        auth_tokens=tokens,
        client_endpoint=client_endpoint
    )
    return user_info['result']


async def get_admin_status(CRest: CRestBitrix24, tokens: AuthTokens, client_endpoint: str) -> bool:
    callreq = CallRequest(method="user.admin")
    result = await CRest.call(
        callreq,
        auth_tokens=tokens,
        client_endpoint=client_endpoint
    )
    return result.get("result")


async def create_ktalk_company_calendar(
    crest: CRestBitrix24,
    user_auth: UserAuthModel,
    calendar_name: str = CALENDAR_NAME,
) -> CALENDAR_ID:
    """
    Создать календарь компании, общий для всех сотрудников.
    Нет проверки на то, существует ли уже такой календарь.
    """
    tokens = AuthTokens(
        **user_auth.model_dump()
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
        client_endpoint=user_auth.client_endpoint,
        auth_tokens=tokens
    )
    return result['result']


async def get_ktalk_company_calendar(
    crest: CRestBitrix24,
    user_auth: UserAuthModel,
    calendar_name: str = CALENDAR_NAME,
    calendar_id: CALENDAR_ID = None
) -> BitrixCalendarModel | None:
    tokens = AuthTokens(
        **user_auth.model_dump()
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
        client_endpoint=user_auth.client_endpoint,
        auth_tokens=tokens)

    if not calendar_id and not calendar_name:
        logger.error(
            "Ошибка. Чтобы получить календарь, необходимо передать calendar_name и/или calendar_id")
        return None

    for calendar in result['result']:
        if calendar_id and calendar_name:
            if calendar['ID'] == str(calendar_id) and calendar['NAME'] == calendar_name:
                return BitrixCalendarModel(**calendar)
        elif calendar_id:
            if calendar['ID'] == str(calendar_id):
                return BitrixCalendarModel(**calendar)
        elif calendar_name:
            if calendar['NAME'] == calendar_name:
                return BitrixCalendarModel(**calendar)

    return None


async def create_ktalk_calendar_event(
    crest: CRestBitrix24,
    calendar_id: CALENDAR_ID,
    meeting: MeetingModel,
    created_meeting_information: KTalkBackAnswerModel,
    user_auth: UserAuthModel
) -> CALENDAR_EVENT_ID:
    description = f"{meeting.description}\n\nСсылка на встречу: {created_meeting_information.url}\nПин-код: {meeting.pinCode}".lstrip()

    tokens = AuthTokens(
        **user_auth.model_dump()
    )
    call = CallRequest(
        method='calendar.event.add',
        params={
            'type': 'company_calendar',
            'ownerId': 0,
            'from_ts': meeting.start_robot(False) / 1000,
            'to_ts': meeting.end_robot(False) / 1000,
            'section': calendar_id,
            'name': meeting.subject,
            'description': description
        }
    )
    logger.debug(call)
    result = await crest.call(
        request=call,
        client_endpoint=user_auth.client_endpoint,
        auth_tokens=tokens
    )
    return result['result']


async def get_calendar_event(
    crest: CRestBitrix24,
    calendar_id: CALENDAR_ID,
    calendar_event_id: CALENDAR_EVENT_ID,
    user_auth: UserAuthModel
) -> dict | None:
    tokens = AuthTokens(
        **user_auth.model_dump()
    )
    call = CallRequest(
        method='calendar.event.get',
        params={
            'type': 'company_calendar',
            'ownerId': "0",
            'section': [calendar_id],
        }
    )
    result = await crest.call(
        request=call,
        client_endpoint=user_auth.client_endpoint,
        auth_tokens=tokens
    )
    for meeting in result['result']:
        print(f"{calendar_event_id} - {meeting['ID']}")
        if meeting['ID'] == str(calendar_event_id):
            return (meeting)
    return None


async def send_notification_to_blogpost(
    crest: CRestBitrix24,
    meeting: MeetingModel,
    created_meeting_information: KTalkBackAnswerModel,
    user_auth: UserAuthModel
) -> dict:
    tokens = AuthTokens(
        **user_auth.model_dump()
    )

    base_domain = _get_base_domain_from_client_endpoint(user_auth.client_endpoint)

    logger.debug(created_meeting_information.url)

    message_text = MessageText.format(
        subject=meeting.subject,
        description=meeting.description,
        meeting_url=created_meeting_information.url,
        pin_code=meeting.pinCode,
        calendar_url=base_domain + '/calendar'
    )

    call = CallRequest(
        method="log.blogpost.add",
        params={
            "POST_TITLE": f"Тема: {meeting.subject}",
            "POST_MESSAGE": f"Создана видеоконференция на платформе КТолк\n{message_text}"
        }
    )

    result = await crest.call(
        request=call,
        auth_tokens=tokens,
        client_endpoint=user_auth.client_endpoint
    )
    
    return result


def _get_base_domain_from_client_endpoint(cliend_endpoint: str) -> str:
    return cliend_endpoint.split("/rest/")[0]


async def create_robot_request(
    CRest: CRestBitrix24,
    user_auth: UserAuthModel,
    application_domain: str
) -> dict:
    req = CallRequest(
        method="bizproc.robot.add",
        params={
            'CODE': 'ktalk_robot',
            'HANDLER': f'https://{application_domain}/create-external-meeting',
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
                    "name": "Разница от МСК (например, -2, 0 или 6)",
                    "type": "int",
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
    )
    result = await CRest.call(
        request=req,
        client_endpoint=user_auth.client_endpoint,
        auth_tokens=AuthTokens(
            **user_auth.model_dump()
        )
    )
    if 'error' in result.keys():
        if result['error'] == 'ERROR_METHOD_NOT_FOUND':
            logger.warning("Не удалось создать робота из-за тарифа портала")
        elif result['error'] == 'ERROR_ACTIVITY_ALREADY_INSTALLED':
            logger.warning("Робот уже установлен")
        return result
    return result


async def delete_robot_request(
    crest: CRestBitrix24,
    user_auth: UserAuthModel
):
    req = CallRequest(
        method="bizproc.robot.delete",
        params={
            "CODE": "ktalk_robot"
        }
    )
    result = await crest.call(
        request=req,
        client_endpoint=user_auth.client_endpoint,
        auth_tokens=AuthTokens(
            **user_auth.model_dump()
        )
    )
    if 'error' in result.keys():
        if result['error'] == 'ERROR_ACTIVITY_NOT_FOUND':
            logger.warning("Ошибка при удалении робота. Робот не существует")
        else:
            logger.error(f"Ошибка при удалении робота: {result}")



async def add_todo_activity(
    crest: CRestBitrix24,
    user_auth: UserAuthModel,
    creator_id: int,
    owner_id: int,
    meeting: MeetingModel,
    meeting_url: str,
    # participants: ParticipantsModel = None,
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
            'deadline': meeting.end_ktalk(False),
            'responsibleId': creator_id,
            'settings': [
                {
                    'link': meeting_url,
                    'id': 'link'
                },
                {
                    'from': meeting.start_robot(),
                    'to': meeting.end_robot(),
                    # 'duration': ,
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
    endpoint = user_auth.client_endpoint
    tokens = AuthTokens(
        **user_auth.model_dump()
    )
    response = await crest.call(
        request=call_request,
        client_endpoint=endpoint,
        auth_tokens=tokens
    )
    return response

from typing import AsyncGenerator
from src.db.database import get_session
from src.db.requests import get_portal, get_user_auth_without_model, get_ktalk_space

from fastapi import APIRouter, Depends, Request

from crest.crest import CRestBitrix24
from src.router.utils import get_crest

from src.ktalk.requests import create_meeting
from src.models import PortalModel, KtalkSpaceModel, UserAuthModel
from src.ktalk.models import MeetingModel, KTalkBackAnswerModel
from src.middleware.utils import parse_form_data

from src.bitrix_requests import add_todo_activity

from src.logger.custom_logger import logger

from src.router.utils import format_timezone_from_offset

router = APIRouter()


@router.post("/create-external-meeting")
async def handler(
    request: Request,
    CRest: CRestBitrix24 = Depends(get_crest),
    session: AsyncGenerator = Depends(get_session),
) -> KTalkBackAnswerModel:
    """
    Создание встречи КТолк и дела CRest.
    form:
        "workflow_id": "681b6392a30743.60451827",
        "code": "ktalk_robot",
        "document_id[0]": "crm",
        "document_id[1]": "CCrmDocumentDeal",
        "document_id[2]": "DEAL_18",
        "document_type[0]": "crm",
        "document_type[1]": "CCrmDocumentDeal",
        "document_type[2]": "DEAL",
        "event_token": "681b6392a30743.60451827|A88332_57464_28590_17664|Mr6J9oMP85JGmZ2MG5fLmJNKDYD8PYPc.139d3b428a0b379adadeee279117c4b5e96f1d974987d720cee39f5a91ed7cda",
        "properties[subject]": "Обсуждение документов",
        "properties[description]": "текст!",
        "properties[start]": "04.05.2025 16:15:04",
        "properties[end]": "04.05.2025 01:00:00",
        "properties[timezone]": "gmt+9",  # в новой версии убрал часовой пояс!
        "properties[allowAnonymous]": "Y",
        "properties[enableSip]": "Y",
        "properties[enableAutoRecording]": "Y",
        "properties[pinCode]": "1234",
        "timeout_duration": "0",
        "ts": "1746625426",
        "auth[access_token]": "XXX",
        "auth[expires]": "1746629026",
        "auth[expires_in]": "3600",
        "auth[scope]": "crm,task,user,calendar,placement,log,bizproc",
        "auth[domain]": "XXX",
        "auth[server_endpoint]": "https://oauth.bitrix.info/rest/",
        "auth[status]": "S",
        "auth[client_endpoint]": "XXX",
        "auth[member_id]": "XXX",
        "auth[user_id]": "1",
        "auth[refresh_token]": "XXX",
        "auth[application_token]": "XXX"
    """
    form_json = form_to_json(await request.form())
    auth = form_json.get("auth")
    properties = form_json.get("properties")

    deal_id = form_json['document_id']['2'].split('_')[1]
    user_id = auth['user_id']

    member_id = auth['member_id']

    user_auth: UserAuthModel = await get_user_auth_without_model(session, member_id=member_id, user_id=user_id)
    if not user_auth:
        logger.error(f"Ошибка при получении пользователя: {member_id} - {user_id}")
        return KTalkBackAnswerModel(error='Пользователь не найден')
    
    msk_offset = properties['timezone']
    gmt_timezone = format_timezone_from_offset(msk_offset_hours=msk_offset)
    logger.debug(gmt_timezone)
    properties['timezone'] = gmt_timezone
    logger.debug(properties)
    
    meeting = MeetingModel(**properties)
    logger.debug(meeting)
    logger.debug(meeting.start_robot())
    logger.debug(meeting.start_robot(False))
    logger.debug(meeting.start_ktalk())
    logger.debug(meeting.start_ktalk(False))

    portal: PortalModel = await get_portal(session, member_id)
    if not portal:
        logger.error(f"Ошибка при получении портала: {member_id}")
        return KTalkBackAnswerModel(error='Портал не найден')

    ktalk_space: KtalkSpaceModel = await get_ktalk_space(session=session, portal=portal)
    if not ktalk_space:
        logger.error(f"Ошибка при получении пространства КТолк для портала: {member_id}")
        return KTalkBackAnswerModel(error='Не удалось получить настройки пространства КТолк')

    # === Создание встречи КТолк ===
    ktalk_response: KTalkBackAnswerModel = await create_meeting(
        meeting=meeting,
        ktalk_space=ktalk_space
    )
    if ktalk_response.error:
        logger.error(f"Ошибка при создании встречи КТолк: {ktalk_response.error}")
        return ktalk_response
    logger.info(f'Была создана встреча: {ktalk_response}')
    # ======

    # === Создание дела CRest ===
    activity_result = await add_todo_activity(
        crest=CRest,
        user_auth=user_auth,
        creator_id=user_auth.user_id,
        owner_id=deal_id,
        meeting=meeting,
        meeting_url=ktalk_response.url
    )
    logger.info(f'Было создано дело: {activity_result}')
    # ======

    return ktalk_response


def form_to_json(form_data) -> dict:
    return parse_form_data(form_data)

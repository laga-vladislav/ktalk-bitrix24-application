from typing import AsyncGenerator
from src.db.database import get_session
from src.db.requests import get_portal, get_user_auth_without_model, get_ktalk_space

from fastapi import APIRouter, Depends, Query, Body, Response, HTTPException

from crest.crest import CRestBitrix24
from src.router.utils import get_crest

from src.models import PortalModel, UserAuthModel

from src.bitrix_requests import create_ktalk_calendar_event, get_ktalk_company_calendar, send_notification_to_blogpost
from src.ktalk.requests import create_meeting
from src.ktalk.models import MeetingModel, KTalkBackAnswerModel

from src.logger.custom_logger import logger


router = APIRouter()


@router.post("/create-internal-meeting")
async def handler(
    user_id: int = Query(alias="creatorId"),
    member_id: str = Query(alias="memberId"),
    # user_auth: UserAuthModel = Body(),
    meeting: MeetingModel = Body(),
    # participants: ParticipantsModel,
    CRest: CRestBitrix24 = Depends(get_crest),
    session: AsyncGenerator = Depends(get_session),
) -> KTalkBackAnswerModel:
    """
    Создание внутренней видеоконференции КТолк для сотрудников.
    Создает встречу на платформе КТолк,
    создает встречу в календаре компании,
    отправляет уведомление в ленту о созданной встрече.

    params:
        user_auth: UserAuthModel - данные авторизации пользователя.
        meeting: MeetingModel - данные встречи.
        participants: ParticipantsModel - участники встречи (задел на будущее).
    """
    portal: PortalModel = await get_portal(
        session=session, member_id=member_id
    )
    logger.debug(portal)

    user_auth: UserAuthModel = await get_user_auth_without_model(
        session=session, member_id=member_id, user_id=user_id
    )
    logger.debug(user_auth)

    if not user_auth:
        return HTTPException(400, f"Не найдены данные авторизации для пользователя: {member_id} - {user_id}")

    ktalk_space = await get_ktalk_space(session=session, portal=portal)
    logger.debug(ktalk_space)
    if not ktalk_space:
        logger.error("Пространство КТолк не настроено")
        return HTTPException(400, "Пространство КТолк не настроено")

    created_meeting_information = await create_meeting(meeting=meeting, ktalk_space=ktalk_space)
    logger.debug(created_meeting_information)

    ktalk_calendar = await get_ktalk_company_calendar(
        crest=CRest,
        user_auth=user_auth
    )
    logger.debug(ktalk_calendar)
    if ktalk_calendar:
        await create_ktalk_calendar_event(
            crest=CRest,
            calendar_id=ktalk_calendar.id,
            meeting=meeting,
            created_meeting_information=created_meeting_information,
            user_auth=user_auth
        )
        logger.debug("Успешно создано событие в календаре компании")

        await send_notification_to_blogpost(
            crest=CRest,
            meeting=meeting,
            created_meeting_information=created_meeting_information,
            user_auth=user_auth
        )
        logger.debug("Успешно создан пост в ленте")
    else:
        logger.warning("Календарь компании не был найден")

    return Response(status_code=200)

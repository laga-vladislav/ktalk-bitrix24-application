from typing import AsyncGenerator
from src.db.database import get_session
from src.db.requests import get_portal, get_user

from fastapi import APIRouter, Depends, Query, Body, Response

from crest.crest import CRestBitrix24
from src.router.utils import get_crest

from src.bitrix_requests import get_all_options_bitrix_options, create_ktalk_calendar_event, get_ktalk_company_calendar, get_public_chat, send_notification_message_to_chat
from src.ktalk.requests import create_meeting
from src.ktalk.models import MeetingModel, KTalkBackAnswerModel

from src.logger.custom_logger import logger


router = APIRouter()


@router.post("/create-internal-meeting")
async def handler(
    creator_id: int = Query(alias='creatorId'),
    member_id: str = Query(alias='memberId'),
    meeting: MeetingModel = Body(),
    # participants: ParticipantsModel,
    CRest: CRestBitrix24 = Depends(get_crest),
    session: AsyncGenerator = Depends(get_session),
) -> KTalkBackAnswerModel:
    """
    Создание внутренней встречи КТолк для сотрудников.
    Создает встречу на платформе КТолк,
    создает встречу в календаре компании,
    отправляет уведомление в общий чат о созданной встрече.

    params:
        creatorId: int - user_id из битрикса создателя встречи.
        memberId: str - айди портала.
        meeting: MeetingModel - данные встречи.
        participants: ParticipantsModel - участники встречи (задел на будущее).
    """
    portal = await get_portal(session=session, member_id=member_id)
    user = await get_user(session=session, id=creator_id, member_id=member_id)

    app_options = await get_all_options_bitrix_options(crest_instance=CRest, portal=portal)
    ktalk_calendar = await get_ktalk_company_calendar(crest=CRest, portal=portal, user=user)
    public_chat_id = await get_public_chat(crest=CRest, portal=portal, user=user)

    created_meeting_information = await create_meeting(meeting=meeting, app_options=app_options)

    await create_ktalk_calendar_event(
        crest=CRest,
        calendar_id=ktalk_calendar.id,
        meeting=meeting,
        created_meeting_information=created_meeting_information,
        portal=portal,
        user=user,
    )

    await send_notification_message_to_chat(
        crest=CRest,
        chat_id=public_chat_id,
        meeting=meeting,
        created_meeting_information=created_meeting_information,
        # ktalk_calendar=ktalk_calendar,
        portal=portal,
        user=user
    )

    return Response(status_code=200)

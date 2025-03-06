from typing import AsyncGenerator
from src.db.database import get_session
from src.db.requests import get_portal

from fastapi import APIRouter, Depends, Request

from crest.crest import CRestBitrix24
from src.router.utils import get_crest

from src.bitrix_requests import get_all_options_bitrix_options
from src.ktalk.requests import create_meeting
from src.models import ParticipantsModel
from src.ktalk.models import MeetingModel, KTalkBackAnswerModel
from src.ktalk.utils import get_back_answer

from src.bitrix_requests import add_todo_activity

from src.logger.custom_logger import logger


router = APIRouter()


@router.post("/create-external-meeting")
async def handler(
    request: Request,
    creatorId: int,
    ownerId: int,
    memberId: str,
    meeting: MeetingModel,
    participants: ParticipantsModel,
    CRest: CRestBitrix24 = Depends(get_crest),
    session: AsyncGenerator = Depends(get_session),
) -> KTalkBackAnswerModel:
    """
    Создание встречи КТолк и дела CRest.
    params:
        creatorId: int - user_id из битрикса создателя встречи.
        ownerId: int - айди объекта CRM. Наример, сделки.
        memberId: str - айди портала.
        meeting: MeetingModel - данные встречи.
        participants: ParticipantsModel - участники встречи.
    """
    portal = await get_portal(session, memberId)
    if not portal:
        return KTalkBackAnswerModel(error='Портал не найден')

    # === Создание встречи КТолк ===
    options = await get_all_options_bitrix_options(
        crest_instance=CRest,
        portal=portal
    )
    if not options:
        return KTalkBackAnswerModel(error='Не удалось получить настройки пространства КТолк')

    ktalk_response = await create_meeting(
        meeting=meeting,
        app_options=options
    )
    back_answer_to_front = get_back_answer(
        ktalk_response=ktalk_response, options=options)
    logger.info(f'Была создана встреча: {back_answer_to_front}')
    # ======

    # === Создание дела CRest ===
    activity_result = await add_todo_activity(
        crest=CRest,
        portal=portal,
        creator_id=creatorId,
        owner_id=ownerId,
        meeting=meeting,
        meeting_url=back_answer_to_front.url,
        participants=participants
    )
    logger.info(f'Было создано дело: {activity_result}')
    # ======

    return back_answer_to_front

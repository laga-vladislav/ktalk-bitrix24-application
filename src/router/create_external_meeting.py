from typing import AsyncGenerator
from src.db.database import get_session
from src.db.requests import get_portal, get_user_auth_without_model, get_ktalk_space

from fastapi import APIRouter, Depends, Request

from crest.crest import CRestBitrix24
from src.router.utils import get_crest

from src.ktalk.requests import create_meeting
from src.models import PortalModel, KtalkSpaceModel, UserAuthModel
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
    # participants: ParticipantsModel,
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
    portal: PortalModel = await get_portal(session, memberId)
    if not portal:
        logger.error(f"Ошибка при получении портала: {memberId}")
        return KTalkBackAnswerModel(error='Портал не найден')

    user_auth: UserAuthModel = await get_user_auth_without_model(session, member_id=memberId, user_id=creatorId)
    if not user_auth:
        logger.error(f"Ошибка при получении пользователя: {memberId} - {creatorId}")
        return KTalkBackAnswerModel(error='Пользователь не найден')

    ktalk_space: KtalkSpaceModel = await get_ktalk_space(session=session, portal=portal)
    if not ktalk_space:
        logger.error(f"Ошибка при получении пространства КТолк для портала: {memberId}")
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
        owner_id=ownerId,
        meeting=meeting,
        meeting_url=ktalk_response.url
    )
    logger.info(f'Было создано дело: {activity_result}')
    # ======

    return ktalk_response

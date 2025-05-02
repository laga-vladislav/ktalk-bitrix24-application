from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request, HTTPException
from crest.crest import CRestBitrix24
from src.router.utils import get_crest
from src.ktalk.models import MeetingModel
from src.ktalk.requests import create_meeting
from src.ktalk.utils import get_back_answer
from src.models import PortalModel
from src.middleware.utils import parse_form_data

from src.db.database import get_session
from src.db.requests import get_ktalk_space

from src.bitrix_requests import add_todo_activity

from src.logger.custom_logger import logger


router = APIRouter()


@router.post("/ktalk-robot")
async def handler(
    request: Request,
    CRest: CRestBitrix24 = Depends(get_crest),
    session: AsyncGenerator = Depends(get_session),
):
    form_json = form_to_json(await request.form())

    owner_id = form_json['document_id']['2'].split('_')[1]

    properties = form_json.get("properties")
    meeting = MeetingModel(**properties)

    auth = form_json.get("auth")
    portal = PortalModel(**auth)

    ktalk_space = await get_ktalk_space(session=session, portal=portal)
    if not ktalk_space:
        return HTTPException(500, detail="Настройки КТолк не найдены")

    created_meeting_result = await create_meeting(
        meeting=meeting,
        ktalk_space=ktalk_space
    )
    created_meeting = get_back_answer(created_meeting_result, ktalk_space)
    logger.info(f'Ботом была создана встреча: {created_meeting}')

    if created_meeting.error:
        return HTTPException(500, detail=created_meeting.error)

    todo_activity = await add_todo_activity(
        crest=CRest,
        portal=portal,
        creator_id=auth['user_id'],
        owner_id=owner_id,
        meeting=meeting,
        meeting_url=created_meeting.url,
        participants=...)
    logger.info(todo_activity)
    # TODO: добавить участников в дело, определить, как получать айди сделки. Всё

    return created_meeting


def form_to_json(form_data) -> dict:
    return parse_form_data(form_data)

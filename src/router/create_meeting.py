from typing import AsyncGenerator
from src.db.database import get_session
from src.db.requests import get_portal

from fastapi import APIRouter, Depends, Request

from crest.crest import CRestBitrix24
from crest.models import AuthTokens, CallRequest
from src.models import PortalModel
from src.router.utils import get_crest

from src.ktalk.requests import get_all_options_bitrix_options, create_meeting
from src.ktalk.models import MeetingModel, MeetingStringDateModel, ParticipantsModel, KTalkBackAnswerModel
from src.ktalk.utils import get_back_answer

from src.logger.custom_logger import logger


router = APIRouter()


@router.post("/create_meeting")
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
        member_id: str - айди портала.
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


async def add_todo_activity(
    crest: CRestBitrix24,
    portal: PortalModel,
    creator_id: int,
    owner_id: int,
    meeting: MeetingModel,
    meeting_url: str,
    participants: ParticipantsModel,
    owner_type_id: int = 2
):
    """
    Создать дело внутри объекта CRM.
    owner_id - id объекта CRM. Например, id сделки.
    owner_type_id - тип объекта CRM. Например, 2 - это сделка.
    """
    selected_clients_dicts = [client.model_dump()
                              for client in participants.selectedClients]
    meeting_str_date = MeetingStringDateModel(**dict(meeting))
    print(meeting)
    call_request = CallRequest(
        method="crm.activity.todo.add",
        params={
            'ownerTypeId': owner_type_id,
            'ownerId': owner_id,
            'title': meeting.subject,
            'description': meeting.description,
            'deadline': meeting_str_date.end,
            'responsibleId': creator_id,
            'settings': [
                {
                    'link': meeting_url,
                    'id': 'link'
                },
                {
                    'from': meeting.start,
                    'to': meeting.end,
                    'duration': 1200000,
                    'location': '',
                    'selectedUserIds': participants.colleguesId,
                    'id': 'calendar'
                },
                {
                    'selectedClients': selected_clients_dicts,
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

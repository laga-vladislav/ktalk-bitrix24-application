from fastapi import APIRouter, Depends, Request

from crest.crest import CRestBitrix24
from crest.models import AuthTokens
from src.models import PortalModel
from src.router.utils import get_crest

from src.ktalk.requests import get_all_options_bitrix_options, create_meeting
from src.ktalk.models import MeetingModel, BitrixAppStorageModel, KTalkBackAnswerModel


router = APIRouter()


@router.post("/create_meeting")
async def handler(
    request: Request,
    creatorId: int,
    tokens: AuthTokens,
    meeting: MeetingModel,
    CRest: CRestBitrix24 = Depends(get_crest)
):
    auth = await CRest.refresh_token(refresh_token=tokens.refresh_token)
    portal = PortalModel(**auth)

    options = await get_all_options_bitrix_options(
        crest_instance=CRest,
        portal=portal
    )

    ktalk_response = await create_meeting(
        meeting=meeting,
        app_options=options
    )

    back_answer_to_front = _get_back_answer(
        ktalk_response=ktalk_response, options=options)

    return back_answer_to_front


def _get_meeting_url(ktalk_response: dict, options: BitrixAppStorageModel) -> str:
    url = f'https://{options.space}.ktalk.ru/'
    room = ktalk_response.get('room')
    room_name = room['roomName']
    pin_code = room['pinCode']
    return url + room_name + '?pinCode=' + pin_code


def _get_sip_settings(ktalk_response: dict) -> dict:
    return ktalk_response.get('room')['sipSettings']


def _get_back_answer(ktalk_response: dict, options: BitrixAppStorageModel) -> KTalkBackAnswerModel:
    full_url = _get_meeting_url(ktalk_response=ktalk_response, options=options)
    sip_settings = _get_sip_settings(ktalk_response=ktalk_response)
    return KTalkBackAnswerModel(
        url=full_url, sipSettings=sip_settings
    )

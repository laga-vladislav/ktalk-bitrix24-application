from fastapi import APIRouter, Depends, Form, Request, Query, HTTPException
from fastapi.responses import HTMLResponse

from crest.crest import CRestBitrix24
from src.router.utils import get_crest

from src.ktalk.requests import get_all_options_bitrix_options, create_meeting
from src.ktalk.models import MeetingModel, BitrixAppStorageModel, KTalkBackAnswerModel
from pydantic import ValidationError

from src.logger.custom_logger import logger


router = APIRouter()


@router.post("/create_meeting")
async def handler(
    request: Request,
    creator_id: int,
    options: BitrixAppStorageModel,
    meeting: MeetingModel,
    CRest: CRestBitrix24 = Depends(get_crest)
):
    # # TODO: как получить member_id?
    # # я считаю лучшим вариантом передачу нужной информации с фронта.
    # # Либо фронт может передавать токены, чтобы здесь уже получить настройки
    # options = await get_all_options_bitrix_options(
    #     crest_instance=CRest,
    #     portal=...
    # )
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

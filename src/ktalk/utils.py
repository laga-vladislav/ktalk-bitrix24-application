from datetime import datetime
from src.models import BitrixAppStorageModel
from src.ktalk.models import KTalkBackAnswerModel


def _get_meeting_url(ktalk_response: dict, options: BitrixAppStorageModel) -> str:
    url = f'https://{options.space}.ktalk.ru/'
    room = ktalk_response.get('room')
    room_name = room['roomName']
    try:
        pin_code = room['pinCode']
        return url + room_name + '?pinCode=' + pin_code
    except (KeyError, TypeError):
        return url + room_name


def _get_sip_settings(ktalk_response: dict) -> dict:
    try:
        return ktalk_response.get('room')['sipSettings']
    except KeyError:
        return {}


def get_back_answer(ktalk_response: dict, options: BitrixAppStorageModel) -> KTalkBackAnswerModel:
    full_url = _get_meeting_url(ktalk_response=ktalk_response, options=options)
    sip_settings = _get_sip_settings(ktalk_response=ktalk_response)
    return KTalkBackAnswerModel(
        url=full_url, sipSettings=sip_settings
    ) if sip_settings else KTalkBackAnswerModel(
        url=full_url
    )

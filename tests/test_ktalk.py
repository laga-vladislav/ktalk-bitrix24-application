from environs import Env
from src.models import PortalModel
# from src.bitrix_requests import get_all_options_bitrix_options, set_options_call
from src.db.requests import get_ktalk_space, add_ktalk_space
from src.ktalk.requests import create_meeting
from src.models import KtalkSpaceModel
from src.ktalk.models import MeetingModel
from src.ktalk.utils import get_back_answer

from tests.conftest import crest_auth

env = Env()

option_name = "ktalk_pytest"
option_data = "true"

body = {
    "subject": "Созвон. По будням, в 20:00, только на СТС",
    "description": "Пожалуйста, не подключайтесь!",
    "start": 1741186653000,
    "end": 1741197412000,
    "timezone": "GMT+7",
    "allowAnonymous": True,
    "enableSip": True,
    "enableAutoRecording": True
}

robot_body = {
    "subject": "Созвон. По будням, в 20:00, только на СТС",
    "description": "Пожалуйста, не подключайтесь!",
    "start": "05.09.2024 23:30:23",
    "end": "05.09.2024 23:35:23",
    "timezone": "GMT+9",
    "allowAnonymous": "Y",
    "enableSip": "Y",
    "enableAutoRecording": "Y",
    "pinCode": 1233
}


async def test_create_meeting(get_portal: PortalModel):
    meeting = MeetingModel(**body)
    options = await get_ktalk_space(crest_auth, get_portal)
    result = await create_meeting(meeting, options)
    print(result)
    back_ansswer = get_back_answer(ktalk_response=result, options=options)
    print(back_ansswer)
    assert result

async def test_robot_create_meeting(get_portal: PortalModel):
    meeting = MeetingModel(**robot_body)
    print(meeting)
    options = await get_ktalk_space(crest_auth, get_portal)
    print(options)
    result = await create_meeting(meeting, options)
    print(result)
    back_ansswer = get_back_answer(ktalk_response=result, options=options)
    print(back_ansswer)
    assert result

from environs import Env
from src.models import PortalModel
from src.bitrix_requests import get_all_options_bitrix_options, set_options_call
from src.ktalk.requests import create_meeting
from src.models import AppOptionModel, BitrixAppStorageModel
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


async def test_set_options_for_testing(get_portal: PortalModel):
    """
    Только аднимистратор!
    """
    options = [
        AppOptionModel(option_name='space',
                       option_data=env.str("KTALK_SPACE_NAME")),
        AppOptionModel(option_name='api_key',
                       option_data=env.str("KTALK_API_KEY")),
        AppOptionModel(option_name='admin_email',
                       option_data=env.str("KTALK_ADMIN_EMAIL")),
        AppOptionModel(option_name='member_id',
                       option_data=get_portal.member_id)
    ]
    # Если не работает токен - запусти приложение, чтобы обновить запись в БД. Временная мера
    result = await set_options_call(
        crest_instance=crest_auth,
        portal=get_portal,
        options=options
    )
    print(result)
    assert result


async def test_get_all_options_bitrix_options(get_portal: PortalModel):
    """
    Только аднимистратор!
    """
    result = await get_all_options_bitrix_options(crest_auth, get_portal)
    print(result)
    assert isinstance(result, BitrixAppStorageModel)


async def test_create_meeting(get_portal: PortalModel):
    meeting = MeetingModel(**body)
    options = await get_all_options_bitrix_options(crest_auth, get_portal)
    result = await create_meeting(meeting, options)
    print(result)
    back_ansswer = get_back_answer(ktalk_response=result, options=options)
    print(back_ansswer)
    assert result

async def test_robot_create_meeting(get_portal: PortalModel):
    meeting = MeetingModel(**robot_body)
    print(meeting)
    options = await get_all_options_bitrix_options(crest_auth, get_portal)
    print(options)
    result = await create_meeting(meeting, options)
    print(result)
    back_ansswer = get_back_answer(ktalk_response=result, options=options)
    print(back_ansswer)
    assert result

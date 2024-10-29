from environs import Env
from src.models import PortalModel
from src.ktalk.requests import set_option_call, create_meeting, get_option_value_by_name, get_all_options_bitrix_options, set_options_call, get_all_options_dict
from src.ktalk.models import MeetingModel, AppOptionModel, BitrixAppStorageModel
from src.ktalk.utils import get_back_answer

from src.ktalk.requests import set_options_call

from tests.conftest import crest_auth

env = Env()

option_name = "ktalk_pytest"
option_data = "true"

body = {
    "subject": "Созвон. По будням, в 20:00, только на СТС",
    "description": "Пожалуйста, не подключайтесь!",
    "start": 1724900580000,
    "end": 1724900589000,
    "timezone": "GMT+9",
    "allowAnonymous": True,
    "enableSip": True,
    "pinCode": "",
    "enableAutoRecording": False,
    # "isRecurring": True
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


async def test_set_option_call(get_portal: PortalModel):
    result = await set_option_call(
        crest_instance=crest_auth,
        portal=get_portal,
        option_name=option_name,
        option_data=option_data
    )
    print(result)


async def test_set_options_call(get_portal: PortalModel):
    result = await set_options_call(
        crest_instance=crest_auth,
        portal=get_portal,
        options=[
            AppOptionModel(option_name=option_name, option_data=option_data),
            AppOptionModel(option_name="pytest", option_data="pytest")
        ]
    )
    print(result)


async def test_get_option_true(get_portal: PortalModel):
    result = await get_option_value_by_name(
        crest_instance=crest_auth,
        portal=get_portal,
        option_name=option_name
    )
    assert isinstance(result, str)
    assert result == "true"


async def test_get_option_false(get_portal: PortalModel):
    result = await get_option_value_by_name(
        crest_instance=crest_auth,
        portal=get_portal,
        option_name="sadgfafdsg"
    )
    assert isinstance(result, str)
    assert result == ""


async def test_get_all_options(get_portal: PortalModel):
    result = await get_all_options_dict(
        crest_instance=crest_auth,
        portal=get_portal
    )
    print(result)
    assert isinstance(result, dict)
    assert result.get('pytest') == 'pytest'


async def test_set_options_for_testing(get_portal: PortalModel):
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

async def test_create_meeting_robot_body(get_portal: PortalModel):
    meeting = MeetingModel(**robot_body)
    print(meeting)
    options = await get_all_options_bitrix_options(crest_auth, get_portal)
    print(options)
    result = await create_meeting(meeting, options)
    print(result)
    back_ansswer = get_back_answer(ktalk_response=result, options=options)
    print(back_ansswer)
    assert result

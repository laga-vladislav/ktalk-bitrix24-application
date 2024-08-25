from src.models import PortalModel
from src.ktalk.requests import set_option_call, create_meeting, get_option_value_by_name, get_all_options, set_options_call
from src.ktalk.models import MeetingModel, AppOptionModel

from src.ktalk.requests import set_options_call
from src.ktalk.models import BitrixAppStorageModel
from src.db.requests import get_portal

from tests.conftest import crest_auth

option_name = "ktalk_pytest"
option_data = "true"


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
        option_name="pytest"
    )
    assert isinstance(result, str)
    assert result == ""


async def test_get_all_options(get_portal: PortalModel):
    result = await get_all_options(
        crest_instance=crest_auth,
        portal=get_portal
    )
    assert isinstance(result, dict)
    assert result.get('pytest') == 'pytest'


async def test_get_meeting():
    body = {
        "subject": "Созвон. По будням, в 20:00, только на СТС",
        "description": "Пожалуйста, не подключайтесь!",
        "start": "2024-08-28T03:00:00.000Z",
        "end": "2024-08-28T04:00:00.000Z",
        "timezone": "GMT+9",
        "allowAnonymous": True,
        "enableSip": True,
        "pinCode": "1234",
        "enableAutoRecording": True,
        "isRecurring": False
    }
    meeting = MeetingModel(**body)
    result = await create_meeting(meeting)
    print(result)


async def test_set_options_for_testing(get_portal: PortalModel):
    options = [
        AppOptionModel(option_name='space', option_data='infocom-child'),
        AppOptionModel(option_name='api_key',
                       option_data='b8vyChTvRtVRFbuWD3MPUTrecdxXSQJy'),
        AppOptionModel(option_name='admin_email',
                       option_data='v.laga@infocom.io'),
        AppOptionModel(option_name='member_id',
                       option_data='16fc986a7286f8863682790e8ea9327c')
    ]
    # Если не работает токен запусти приложение, чтобы обновить запись в БД. Временная мера
    result = await set_options_call(
        crest_instance=crest_auth,
        portal=get_portal,
        options=options
    )
    print(result)

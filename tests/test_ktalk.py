from src.models import PortalModel
from src.ktalk.requests import set_option_call, create_meeting, get_option_value_by_name, get_all_options
from src.ktalk.models import MeetingModel

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
    assert result.get("ktalk_pytest") == "true"


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

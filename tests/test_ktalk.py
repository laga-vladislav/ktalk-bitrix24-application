import uuid
from datetime import datetime
from environs import Env
from src.models import PortalModel, UserAuthModel
# from src.bitrix_requests import get_all_options_bitrix_options, set_options_call
from src.db.requests import get_ktalk_space, add_ktalk_space
from src.ktalk.requests import create_meeting
from src.models import KtalkSpaceModel
from src.ktalk.models import MeetingModel, KTalkBackAnswerModel
from src.ktalk.utils import get_back_answer

from tests.conftest import crest_auth
from tests.data import KTalkTestData as data


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


def _is_valid_uuid(value: str) -> bool:
    try:
        uuid_obj = uuid.UUID(value)
        return str(uuid_obj) == value
    except (ValueError, AttributeError, TypeError):
        return False


class Test3KtalkApplication:
    async def test_meeting_model_keys(self):
        meeting_dict = data.meeting_dict.copy()
        meeting_model = data.meeting_model.model_copy()
        model_fields = set(meeting_model.model_fields.keys())
        print(model_fields)
        print(meeting_dict.keys())
        assert all(key in model_fields for key in meeting_dict.keys())


    async def test_meeting_model_private_properties(self):
        meeting_model = data.meeting_model.model_copy()
        
        assert isinstance(meeting_model.start_robot, int)
        assert isinstance(meeting_model.end_robot, int)

        assert isinstance(meeting_model.start_todo_activity, str)
        assert isinstance(meeting_model.end_todo_activity, str)
        assert isinstance(meeting_model.start_ktalk, str)
        assert isinstance(meeting_model.end_ktalk, str)

        assert meeting_model.start_todo_activity
        assert meeting_model.end_todo_activity
        assert meeting_model.start_ktalk
        assert meeting_model.end_ktalk

        datetime.strptime(meeting_model.start_todo_activity, '%d.%m.%Y %H:%M:%S')
        datetime.strptime(meeting_model.end_todo_activity, '%d.%m.%Y %H:%M:%S')
        datetime.strptime(meeting_model.start_ktalk, '%Y-%m-%dT%H:%M:%SZ')
        datetime.strptime(meeting_model.end_ktalk, '%Y-%m-%dT%H:%M:%SZ')


    async def test_create_meeting(self, get_ktalk_space: KtalkSpaceModel):
        meeting_model: MeetingModel = data.meeting_model.model_copy()
        created_meeting: KTalkBackAnswerModel = await create_meeting(
            meeting=meeting_model,
            ktalk_space=get_ktalk_space
        )
        print(created_meeting)
        assert isinstance(created_meeting, KTalkBackAnswerModel)

# async def test_robot_create_meeting(get_portal: PortalModel):
#     meeting = MeetingModel(**robot_body)
#     print(meeting)
#     options = await get_ktalk_space(crest_auth, get_portal)
#     print(options)
#     result = await create_meeting(meeting, options)
#     print(result)
#     back_ansswer = get_back_answer(ktalk_response=result, options=options)
#     print(back_ansswer)
#     assert result

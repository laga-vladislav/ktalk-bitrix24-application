import random
import string
import json
import datetime
import uuid
from pathlib import Path
from dataclasses import dataclass
from src.models import UserModel, KtalkSpaceModel, PortalModel, UserAuthModel
from src.ktalk.models import MeetingModel, KTalkBackAnswerModel


def get_random_string(length: int = 10):
    return ''.join(random.choices(string.ascii_uppercase +
                                  string.digits, k=length))


STORAGE_PATH = Path("tests/data.json")
dt = datetime.datetime.now()
CURRENT_TIMESTAMP_MS = (int(dt.timestamp()) * 1000)

def load_persistent_data():
    if STORAGE_PATH.exists():
        with open(STORAGE_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_persistent_data(data_dict):
    with open(STORAGE_PATH, 'w') as f:
        json.dump(data_dict, f, indent=4)

_persistent_data = load_persistent_data()


@dataclass
class DatabaseTestData:
    """
    Данные, необходимый для тестирования базы данных.
    """
    # Портал
    test_portal_data_dict = {
        'member_id': get_random_string(),
        'client_endpoint': 'client_endpoint',
        'scope': 'scope'
    }
    test_portal_data_model = PortalModel(
        **test_portal_data_dict
    )

    # Пользователь
    test_user_data_dict_correct = {
        'user_id': random.randint(1, 100),
        'member_id': test_portal_data_model.member_id,
        'name': get_random_string(),
        'last_name': get_random_string(),
        'is_admin': random.randint(0, 1)
    }
    test_user_data_model_correct = UserModel(
        **test_user_data_dict_correct
    )
    test_user_data_dict_incorrect = {
        'user_id': random.randint(1, 100),
        'member_id': get_random_string(),
        'name': get_random_string(),
        'last_name': get_random_string(),
        'is_admin': random.randint(0, 1)
    }
    test_user_data_model_incorrect = UserModel(
        **test_user_data_dict_incorrect
    )

    # КТолк пространство
    test_ktalk_space_data_dict_correct = {
        'member_id': test_portal_data_model.member_id,
        'space': get_random_string(),
        'api_key': get_random_string(),
        'admin_email': get_random_string()
    }
    test_ktalk_space_data_model_correct = KtalkSpaceModel(
        **test_ktalk_space_data_dict_correct
    )
    test_ktalk_space_data_dict_incorrect = {
        'member_id': get_random_string(),
        'space': get_random_string(),
        'api_key': get_random_string(),
        'admin_email': get_random_string()
    }
    test_ktalk_space_data_model_incorrect = KtalkSpaceModel(
        **test_ktalk_space_data_dict_incorrect
    )

    # Токены
    test_user_auth_data_dict_correct = {
        'user_id': test_user_data_model_correct.user_id,
        'member_id': test_user_data_model_correct.member_id,
        'access_token': get_random_string(),
        'refresh_token': get_random_string(),
        'client_endpoint': test_portal_data_model.client_endpoint
    }
    test_user_auth_data_model_correct = UserAuthModel(
        **test_user_auth_data_dict_correct
    )
    test_user_auth_data_dict_incorrect = {
        'user_id': random.randint(1, 100),
        'member_id': get_random_string(),
        'access_token': get_random_string(),
        'refresh_token': get_random_string(),
        'client_endpoint': get_random_string()
    }
    test_user_auth_data_model_incorrect = UserAuthModel(
        **test_user_auth_data_dict_incorrect
    )
    

@dataclass
class KTalkTestData:
    meeting_dict = {
        "subject": "Созвон. По будням, в 20:00, только на СТС",
        "description": "Пожалуйста, не подключайтесь!",
        "start": CURRENT_TIMESTAMP_MS,
        "end": CURRENT_TIMESTAMP_MS + 5000000,
        "timezone": "GMT+9",
        "allowAnonymous": True,
        "enableSip": True,
        "enableAutoRecording": True,
        "roomName": str(uuid.uuid4())
    }
    meeting_model = MeetingModel(**meeting_dict)
    meeting_information_back_answer = KTalkBackAnswerModel(
        url='example.com'
    )


@dataclass
class BitrixTestData:
    calendar_name: str = 'Календарь встреч КТолк'
    calendar_id: int = _persistent_data.get("calendar_id")
    meeting_id: int = _persistent_data.get("meeting_id")
    company_id: int = _persistent_data.get("company_id")
    contact_id: int = _persistent_data.get("contact_id")
    deal_id: int = _persistent_data.get("deal_id")

    @staticmethod
    def save():
        save_persistent_data({
            "calendar_id": BitrixTestData.calendar_id,
            "meeting_id": BitrixTestData.meeting_id,
            "company_id": BitrixTestData.company_id,
            "contact_id": BitrixTestData.contact_id,
            "deal_id": BitrixTestData.deal_id
        })
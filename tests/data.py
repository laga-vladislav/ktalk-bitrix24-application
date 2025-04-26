import random
import string
from dataclasses import dataclass
from src.models import UserModel, KtalkSpaceModel, PortalModel, UserAuthModel


def get_random_string(length: int = 10):
    return ''.join(random.choices(string.ascii_uppercase +
                                  string.digits, k=length))


@dataclass
class DatabaseTestData:
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
    
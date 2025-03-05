import os
import datetime
import jwt
from src.models import UserModel
from src.logger.custom_logger import logger

SECRET_KEY = os.getenv("JWT_KEY")


def create_jwt(user: UserModel) -> str:
    payload = {
        **user.model_dump(mode="json"),
        "exp": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)).timestamp()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("JWT токен просрочен")
        return None
    except jwt.InvalidTokenError:
        logger.error("JWT токен поврежден")
        return None

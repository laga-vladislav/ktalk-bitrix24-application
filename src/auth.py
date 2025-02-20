import os
import datetime
import jwt
from src.models import UserModel

SECRET_KEY = os.getenv("JWT_KEY")


def create_jwt(user: UserModel) -> str:
    payload = {
        **user.model_dump(mode="json"),
        "exp": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)).timestamp()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

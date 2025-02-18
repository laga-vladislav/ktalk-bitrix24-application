import os
import datetime
import jwt
from models import UserModel

SECRET_KEY = os.getenv("JWT_KEY")


def create_jwt(user):
    payload = {
        "id": user.id,
        "isAdmin": user.is_admin,
        "exp": datetime.utcnow() + datetime.timedelta(hours=2)  # токен живет 2 часа
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload  # Возвращает данные (например, id пользователя)
    except jwt.ExpiredSignatureError:
        return None  # Токен истек
    except jwt.InvalidTokenError:
        return None  # Токен сломан

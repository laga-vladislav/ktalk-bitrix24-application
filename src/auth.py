import os
import datetime
import jwt 
from fastapi import HTTPException
from src.models import UserAuthModel
from src.logger.custom_logger import logger

SECRET_KEY = os.getenv("JWT_KEY")


def create_jwt(user_auth: UserAuthModel, lifetime_in_hours: int = 1) -> str:
    payload = {
        **user_auth.model_dump(mode="json"),
        "exp": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=lifetime_in_hours)).timestamp()
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


async def get_current_user(authorization: str):
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401, detail="Invalid authorization scheme")

    token_data = verify_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token_data

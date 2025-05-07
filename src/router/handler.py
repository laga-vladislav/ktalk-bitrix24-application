import os
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from src.auth import create_jwt
from crest.crest import CRestBitrix24
from crest.models import AuthTokens, CallRequest
from src.models import UserModel, UserAuthModel

from src.db.database import get_session
from src.db.requests import get_user, add_user, get_user_auth, set_user_auth

from src.router.utils import get_crest
from src.bitrix_requests import get_user_info
from src.logger.custom_logger import logger

router = APIRouter()


@router.post("/handler")
async def handler(
    request: Request,
    CRest: CRestBitrix24 = Depends(get_crest),
    REFRESH_ID: str = Form(..., alias="REFRESH_ID"),
    session: AsyncGenerator = Depends(get_session),
):
    full_auth = await CRest.refresh_token(REFRESH_ID)
    logger.debug(full_auth)

    user: UserModel | None = await get_user(
        session=session,
        user_id=full_auth['user_id'],
        member_id=full_auth['member_id']
    )

    if not user:
        await _add_user(
            CRest=CRest, session=session, user_auth=full_auth
        )
        user = await get_user(
            session=session,
            user_id=full_auth['user_id'],
            member_id=full_auth['member_id']
        )

    user_auth: UserAuthModel | None = await get_user_auth(
        session=session,
        user=user
    )

    if not user_auth:
        user_auth = UserAuthModel(
            user_id=user.user_id,
            member_id=user.member_id,
            client_endpoint=full_auth['client_endpoint'],
            access_token=full_auth['access_token'],
            refresh_token=full_auth['refresh_token']
        )

    (user_auth.access_token, user_auth.refresh_token) = (full_auth['access_token'], full_auth['refresh_token'])
    await set_user_auth(session=session, auth=user_auth)

    token = create_jwt(user=user)

    redirect_url = f"https://{os.getenv("FRONT_DOMAIN")}"
    if user.is_admin:
        redirect_url += "/menu"
    else:
        redirect_url += "/create-meeting"
    redirect_url += "?token=" + token

    response = RedirectResponse(url=redirect_url)

    return response


@router.head("/handler")
async def head_handler():
    return


async def _add_user(CRest: CRestBitrix24, session: AsyncGenerator, user_auth: dict):
    user = await get_user_info(
        CRest=CRest,
        tokens=AuthTokens(access_token=user_auth['access_token'], refresh_token=user_auth['refresh_token']),
        client_endpoint=user_auth["client_endpoint"],
        member_id=user_auth["member_id"]
    )
    logger.debug(user)

    await add_user(
        session=session,
        user=user
    )
    
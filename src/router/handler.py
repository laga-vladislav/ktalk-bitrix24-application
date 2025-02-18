from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from crest.crest import CRestBitrix24
from crest.models import AuthTokens, CallRequest
from src.models import UserModel

from src.db.database import get_session
from src.db.requests import add_user

from src.router.utils import get_crest
from src.logger.custom_logger import logger


router = APIRouter()


@router.post("/handler")
async def handler(
    request: Request,
    CRest: CRestBitrix24 = Depends(get_crest),
    user_refresh_token: str = Form(..., alias="REFRESH_ID"),
    session: AsyncGenerator = Depends(get_session),
):
    full_auth = await CRest.refresh_token(user_refresh_token)
    logger.debug(full_auth)

    user_tokens = AuthTokens(
        access_token=full_auth["access_token"], refresh_token=full_auth["refresh_token"]
    )

    user = await get_user_info(
        CRest=CRest,
        tokens=user_tokens,
        client_endpoint=full_auth["client_endpoint"],
        member_id=full_auth["member_id"]
    )
    logger.debug(user)

    await add_user(
        session=session,
        user=user
    )

    if user.is_admin:
        return HTMLResponse("<h1>Страница для администратора</h1>")
    else:
        return HTMLResponse("<h1>Страница для пользователя</h1>")


async def get_user_info(CRest: CRestBitrix24, tokens: AuthTokens, client_endpoint: str, member_id: str) -> UserModel:
    inforeq = CallRequest(method="user.current")
    user_info = await CRest.call(
        request=inforeq,
        auth_tokens=tokens,
        client_endpoint=client_endpoint
    )
    is_admin = await get_admin_status(CRest, tokens, client_endpoint)
    return UserModel(
        member_id=member_id,
        id=user_info['result']['ID'],
        name=user_info['result']['NAME'],
        last_name=user_info['result']['LAST_NAME'],
        is_admin=is_admin,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token
    )


async def get_admin_status(CRest: CRestBitrix24, tokens: AuthTokens, client_endpoint: str) -> bool:
    callreq = CallRequest(method="user.admin")
    result = await CRest.call(
        callreq,
        auth_tokens=tokens,
        client_endpoint=client_endpoint
    )
    return result.get("result")


@router.head("/handler")
async def head_handler():
    return

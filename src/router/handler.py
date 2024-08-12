from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from crest.crest import CRestBitrix24
from crest.models import AuthTokens
from src.router.utils import get_crest
from src.db.database import get_session
from src.db.requests import get_portal
from src.db.schemes import PortalScheme

router = APIRouter()


@router.post("/handler")
async def handler(
    request: Request,
    CRest: CRestBitrix24 = Depends(get_crest),
    user_refresh_token: str = Form(..., alias="REFRESH_ID"),
    # user_access_token: str = Form(..., alias="AUTH_ID"),
):
    pass
    # newauth = await CRest.refresh_token(user_refresh_token)
    # user_access_token = newauth["access_token"]
    # user_refresh_token = newauth["refresh_token"]

    # callreq = CallRequest(method="user.admin")
    # result = await CRest.call(callreq, client_endpoint=newauth["client_endpoint"], access_token=user_access_token)

    # return result


@router.head("/handler")
async def head_handler():
    return

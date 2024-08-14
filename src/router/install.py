from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from crest.crest import CRestBitrix24
from crest.models import AuthTokens, CallRequest
from src.db.database import get_session
from src.db.models import PortalModel
from src.db.requests import get_portal, add_portal, refresh_portal
from src.router.utils import get_crest

from src.logger.custom_logger import logger

router = APIRouter()


@router.post("/install")
async def install(
    request: Request,
    CRest: CRestBitrix24 = Depends(get_crest),
    admin_refresh_token: str = Form(..., alias="REFRESH_ID"),
    session: AsyncGenerator = Depends(get_session),
):
    html_content = """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <title>Installation</title>
            <script src="//api.bitrix24.com/api/v1/"></script>
            <script>
                BX24.init(function(){
                    BX24.installFinish();
                });
            </script>
        </head>
        <body>
            <p>Installation finished</p>
        </body>
        </html>
    """

    # Получаем обширную информацию с новыми токенами
    new_auth = await CRest.refresh_token(refresh_token=admin_refresh_token)

    # ищем портал
    portal = await get_portal(session, new_auth["member_id"])
    if portal:
        portal.access_token = new_auth["access_token"]
        portal.refresh_token = new_auth["refresh_token"]
        await refresh_portal(session, portal)
    else:
        portal = PortalModel(
            member_id=new_auth["member_id"],
            endpoint=new_auth["endpoint"],
            scope=new_auth["scope"],
            access_token=new_auth["access_token"],
            refresh_token=new_auth["refresh_token"]
        )
        await add_portal(session, new_auth)

    admin_tokens = AuthTokens(
        access_token=new_auth["access_token"], refresh_token=new_auth["refresh_token"]
    )

    params = {
        "PLACEMENT": "CRM_DEAL_DETAIL_ACTIVITY",
        "HANDLER": str(request.base_url) + "placement/crm_deal",
        "TITLE": "КТолк",
    }
    callreq = CallRequest(method="placement.bind", params=params)

    result = await CRest.call(
        callreq, client_endpoint=new_auth["client_endpoint"], auth_tokens=admin_tokens
    )

    is_done = result.get("result")
    if is_done:
        logger.info("Установка виджетов прошла успешно")
    else:
        logger.info("Виджеты были уже установлены")

    return HTMLResponse(content=html_content, status_code=200)


@router.head("/install")
async def head_install():
    return

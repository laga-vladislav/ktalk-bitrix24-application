from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from crest.crest import CRestBitrix24
from crest.models import AuthTokens, CallRequest
from src.db.database import get_session
from src.models import PortalModel
from src.db.requests import get_portal, add_portal, refresh_portal
from src.router.utils import get_crest
from src.bitrix_requests import get_ktalk_company_calendar, create_ktalk_company_calendar, create_robot_request

from src.logger.custom_logger import logger

from environs import Env

env = Env()

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
    print(new_auth)

    # ищем портал
    portal = await get_portal(session, new_auth["member_id"])
    if portal:
        portal.access_token = new_auth["access_token"]
        portal.refresh_token = new_auth["refresh_token"]
        await refresh_portal(session, portal)
    else:
        portal = PortalModel(
            member_id=new_auth["member_id"],
            client_endpoint=new_auth["client_endpoint"],
            scope=new_auth["scope"],
            access_token=new_auth["access_token"],
            refresh_token=new_auth["refresh_token"]
        )
        await add_portal(session, portal)

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
        logger.debug(is_done)
    else:
        logger.info("Виджеты были уже установлены")

    already_created_calendar = await get_ktalk_company_calendar(
        crest=CRest,
        portal=portal
    )
    if already_created_calendar:
        logger.info("Календарь КТолк уже существует")
    else:
        created_calendar = await create_ktalk_company_calendar(
            crest=CRest,
            portal=portal
        )
        if created_calendar:
            logger.info("Календарь КТолк успешно создан")
            logger.debug(created_calendar)
        else:
            logger.error("Ошибка при создании календаря КТолк")

    created_robot = await create_robot_request(
        CRest=CRest,
        portal=portal,
        application_domain=env.str("APPLICATION_DOMAIN")
    )
    if created_robot:
        logger.info("Робот был создан")
        logger.debug(created_robot)
    else:
        logger.info("Робот уже был создан")

    return HTMLResponse(content=html_content, status_code=200)


@router.head("/install")
async def head_install():
    return

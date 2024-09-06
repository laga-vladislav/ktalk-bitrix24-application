from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from crest.crest import CRestBitrix24
from crest.models import AuthTokens, CallRequest
from src.db.database import get_session
from src.models import PortalModel
from src.db.requests import get_portal, add_portal, refresh_portal
from src.router.utils import get_crest

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
    else:
        logger.info("Виджеты были уже установлены")

    robot_created = await create_robot_request(
        CRest=CRest,
        portal=portal,
        application_domain=env.str("APPLICATION_DOMAIN")
    )
    logger.info(robot_created)
    if robot_created:
        logger.info("Робот был создан")
    else:
        logger.info("Робот уже был создан")

    return HTMLResponse(content=html_content, status_code=200)


@router.head("/install")
async def head_install():
    return


async def _get_portal(session, auth) -> PortalModel:
    portal = await get_portal(session, auth["member_id"])
    if portal:
        portal.access_token = auth["access_token"]
        portal.refresh_token = auth["refresh_token"]
        await refresh_portal(session, portal)
    else:
        portal = PortalModel(
            member_id=auth["member_id"],
            client_endpoint=auth["client_endpoint"],
            scope=auth["scope"],
            access_token=auth["access_token"],
            refresh_token=auth["refresh_token"]
        )
        await add_portal(session, portal)

async def create_robot_request(
    CRest: CRestBitrix24,
    portal: PortalModel,
    application_domain: str
):
    return await CRest.call(
        CallRequest(
            method="bizproc.robot.add",
            params={
                'CODE': 'ktalk_robot',
                'HANDLER': f'{application_domain}/ktalk_robot',
                'AUTH_USER_ID': 1,
                'NAME': 'Робот КТолк',
                "PROPERTIES": {
                    "subject": {
                        "name": "Тема встречи",
                        "type": "string",
                        "required": "Y"
                    },
                    "description": {
                        "name": "Текст приглашения",
                        "type": "string",
                        "required": "Y"
                    },
                    "start": {
                        "name": "Дата и время начала",
                        "type": "datetime",
                        "required": "Y"
                    },
                    "end": {
                        "name": "Дата и время окончания",
                        "type": "datetime",
                        "required": "Y"
                    },
                    "timezone": {
                        "name": "Часовой пояс",
                        "type": "string",
                        "required": "Y"
                    },
                    "allowAnonymous": {
                        "name": "Подключение внешних пользователей",
                        "type": "bool",
                        "required": "Y"
                    },
                    "enableSip": {
                        "name": "Подключение по звонку",
                        "type": "bool",
                        "required": "Y"
                    },
                    "enableAutoRecording": {
                        "name": "Автоматическая запись встречи",
                        "type": "bool",
                        "required": "Y"
                    },
                    "pinCode": {
                        "name": "Pin-код (от 4 до 6 цифр)",
                        "type": "int",
                        "required": "N"
                    }
                }
            }
        ),
        client_endpoint=portal.client_endpoint,
        auth_tokens=AuthTokens(
            access_token=portal.access_token,
            refresh_token=portal.refresh_token
        )
    )

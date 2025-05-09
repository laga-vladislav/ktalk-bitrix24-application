from datetime import datetime

from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from crest.crest import CRestBitrix24
from crest.models import AuthTokens, CallRequest
from src.db.database import get_session
from src.models import PortalModel, UserModel, UserAuthModel
from src.db.requests import get_portal, add_portal, add_user, get_user, set_user_auth, get_user_auth
from src.router.utils import get_crest
from src.bitrix_requests import get_ktalk_company_calendar, create_ktalk_company_calendar, create_robot_request, get_user_info

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
    admin_request: dict = await CRest.refresh_token(refresh_token=admin_refresh_token)
    logger.debug(admin_request)

    # Если портал не найден, то сначала добавим его
    portal = await get_portal(session, admin_request['member_id'])
    if not portal:
        portal = PortalModel(
            member_id=admin_request["member_id"],
            client_endpoint=admin_request["client_endpoint"],
            scope=admin_request["scope"],
        )
        await add_portal(session, portal)
    
    # На данном этапе мы можем гарантировать, что портал существует в БД
    admin_user: UserModel = await get_user(session=session, user_id=admin_request['user_id'], member_id=admin_request['member_id'])
    logger.debug(admin_user)

    # Имеется портал, но пользователь, который установил приложение
    # не находится в БД. Тогда сначала добавим его.
    if not admin_user:
        user = await get_user_info(
            CRest=CRest,
            tokens=AuthTokens(access_token=admin_request['access_token'], refresh_token=admin_request['refresh_token']),
            client_endpoint=admin_request["client_endpoint"],
            member_id=admin_request["member_id"]
        )
        logger.debug(user)

        await add_user(
            session=session,
            user=user
        )
        admin_user: UserModel = user

    # Получив пользователя из БД, обновим данные авторизации
    admin_user_auth: UserAuthModel = await get_user_auth(session=session, user=admin_user)
    if not admin_user_auth:
        admin_user_auth = UserAuthModel(
            user_id=admin_user.user_id,
            member_id=admin_user.member_id,
            client_endpoint=portal.client_endpoint,
            access_token="temp_access_token",
            refresh_token="temp_refresh_token"
        )
    (admin_user_auth.access_token, admin_user_auth.refresh_token, admin_user_auth.updated_at) = (admin_request['access_token'], admin_request['refresh_token'], datetime.now())
    
    await set_user_auth(session=session, auth=admin_user_auth)

    admin_tokens = AuthTokens(
        access_token=admin_user_auth.access_token, refresh_token=admin_user_auth.refresh_token
    )

    # Встройка
    params = {
        "PLACEMENT": "CRM_DEAL_DETAIL_ACTIVITY",
        "HANDLER": str(request.base_url) + "placement/crm_deal",
        "TITLE": "КТолк видеоконференции",
    }
    callreq = CallRequest(method="placement.bind", params=params)

    result = await CRest.call(
        request=callreq,
        client_endpoint=admin_user_auth.client_endpoint,
        auth_tokens=admin_tokens
    )

    is_done = result.get("result")
    if is_done:
        logger.info("Установка виджетов прошла успешно")
        logger.debug(is_done)
    else:
        logger.info("Виджеты были уже установлены")

    # Календарь
    already_created_calendar = await get_ktalk_company_calendar(
        crest=CRest,
        user_auth=admin_user_auth
    )
    if already_created_calendar:
        logger.info("Календарь КТолк уже существует")
    else:
        created_calendar = await create_ktalk_company_calendar(
            crest=CRest,
            user_auth=admin_user_auth
        )
        if created_calendar:
            logger.info("Календарь КТолк успешно создан")
            logger.debug(created_calendar)
        else:
            logger.error("Ошибка при создании календаря КТолк")

    # Робот
    created_robot = await create_robot_request(
        CRest=CRest,
        user_auth=admin_user_auth,
        application_domain=env.str("APPLICATION_DOMAIN")
    )
    if not 'error' in created_robot.keys():
        logger.warning(f"Ошибка при создании робота: {created_robot}")

    return HTMLResponse(content=html_content, status_code=200)


@router.head("/install")
async def head_install():
    return

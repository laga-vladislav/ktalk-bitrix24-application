from httpx import AsyncClient

from crest.crest import CRestBitrix24
from crest.models import CallRequest, AuthTokens
from src.ktalk.models import MeetingModel, BitrixAppStorageModel, AppOptionModel
from src.models import PortalModel


async def set_option_call(
    crest_instance: CRestBitrix24,
    portal: PortalModel,
    option_name: str,
    option_data: str
):
    endpoint = portal.client_endpoint
    tokens = AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    response = await crest_instance.call(
        CallRequest(
            method="app.option.set",
            params={
                'options': {
                    option_name: option_data
                }
            }
        ),
        client_endpoint=endpoint,
        auth_tokens=tokens
    )
    return response


async def set_options_call(
    crest_instance: CRestBitrix24,
    portal: PortalModel,
    options: list[AppOptionModel]
):
    endpoint = portal.client_endpoint
    tokens = AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    params = {
        'options': {}
    }
    for option in options:
        params['options'][option.option_name] = option.option_data

    request = CallRequest(
        method="app.option.set",
        params=params
    )

    response = await crest_instance.call(
        request,
        client_endpoint=endpoint,
        auth_tokens=tokens
    )
    return response


async def get_option_value_by_name(
    crest_instance: CRestBitrix24,
    portal: PortalModel,
    option_name: str
) -> str:
    endpoint = portal.client_endpoint
    tokens = AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    response = await crest_instance.call(
        CallRequest(
            method="app.option.get",
            params={
                'option': option_name
            }
        ),
        client_endpoint=endpoint,
        auth_tokens=tokens
    )
    return response.get('result') if response.get('result') else ''


async def get_all_options_dict(
    crest_instance: CRestBitrix24,
    portal: PortalModel
) -> dict:
    endpoint = portal.client_endpoint
    tokens = AuthTokens(
        access_token=portal.access_token,
        refresh_token=portal.refresh_token
    )

    response = await crest_instance.call(
        CallRequest(
            method="app.option.get"
        ),
        client_endpoint=endpoint,
        auth_tokens=tokens
    )
    return dict(response.get('result')) if response.get('result') else {}


async def get_all_options_bitrix_options(
    crest_instance: CRestBitrix24,
    portal: PortalModel
) -> BitrixAppStorageModel | None:
    options = await get_all_options_dict(
        crest_instance=crest_instance,
        portal=portal
    )
    return BitrixAppStorageModel(**dict(options)) if options else None


async def create_meeting(meeting: MeetingModel, app_options: BitrixAppStorageModel) -> dict:
    async with AsyncClient() as client:
        meeting.start = meeting.start_ktalk
        meeting.end = meeting.end_ktalk
        print(meeting.model_dump())

        space_name = app_options.space
        email = app_options.admin_email
        api_key = app_options.api_key

        response = await client.post(
            url=f"https://{space_name}.ktalk.ru/api/emailCalendar/{email}",
            headers={"X-Auth-Token": api_key},
            json=meeting.model_dump()
        )
        response.raise_for_status()
        return response.json()

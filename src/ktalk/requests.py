from httpx import AsyncClient

from crest.crest import CRestBitrix24
from crest.models import CallRequest, AuthTokens
from src.ktalk.models import MeetingModel, BitrixKTalkStorageModel
from src.models import PortalModel


async def set_option_call(
    crest_instance: CRestBitrix24,
    portal: PortalModel,
    option_name: str,
    option_data: str
):
    endpoint = portal.endpoint
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


async def get_option_value_by_name(
    crest_instance: CRestBitrix24,
    portal: PortalModel,
    option_name: str
) -> str:
    endpoint = portal.endpoint
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


async def get_all_options(
    crest_instance: CRestBitrix24,
    portal: PortalModel
) -> dict:
    endpoint = portal.endpoint
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


async def create_meeting(meeting: MeetingModel) -> None:
    ktalk_storage = await get_storage(1, "ktalk")

    async with AsyncClient() as client:
        space_name = ktalk_storage.space
        email = ktalk_storage.admin_email
        api_key = ktalk_storage.api_key

        response = await client.post(
            url=f"https://{space_name}.ktalk.ru/api/emailCalendar/{email}",
            headers={"X-Auth-Token": api_key},
            json=dict(meeting),
        )
        response.raise_for_status()
        return response.json()


async def get_storage(creator_id: int, storage_name: str) -> BitrixKTalkStorageModel:
    return BitrixKTalkStorageModel(**{"space": "infocom-child",
                                      "api_key": "b8vyChTvRtVRFbuWD3MPUTrecdxXSQJy",
                                      "admin_email": "v.laga@infocom.io",
                                      "member_id": "16fc986a7286f8863682790e8ea9327c"})

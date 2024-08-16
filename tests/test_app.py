import asyncio

from httpx import AsyncClient
from src.db.models import PortalModel
from tests.conftest import crest_webhook, crest_auth
from crest.models import CallRequest, AuthTokens


async def test_contact_add_method_webhook():
    call_request = CallRequest(method="crm.contact.add", params={
                               "fields": {'name': 'pytest'}})
    for i in range(2):
        result = await crest_webhook.call(request=call_request)
        print(f"Method: '{call_request.method}'. Attempt # {
              i}. Result: {result}\n")


# async def test_install_post(ac: AsyncClient, admin_refresh_token: str = '8fd9e66600704ff20070536200000001706207b51c5041ac22f9cb2585ae286730e85f'):
#     result = await ac.post("/install", data={
#         "REFRESH_ID": admin_refresh_token})
#     print(result)


async def test_contact_add_method_auth_batch(get_portal: PortalModel):
    call_requests = [
        CallRequest(
            method="crm.contact.add",
            params={
                "fields": {'name': 'pytest_batch'}
            }
        )
        for i in range(70)
    ]

    result = await crest_auth.call_batch(
        call_requests,
        client_endpoint=get_portal.endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token),
    )
    print(result)
    assert isinstance(result, list)

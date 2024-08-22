import asyncio

from datetime import datetime, timedelta

from httpx import AsyncClient
from src.db.models import PortalModel
from tests.conftest import crest_webhook, crest_auth
from crest.models import CallRequest, AuthTokens


async def test_add_robot_auth(get_portal: PortalModel):
    result = await crest_auth.call(
        CallRequest(
            method="bizproc.robot.add",
            params={
                'CODE': 'robot',
                'HANDLER': 'https://firstly-climbing-goat.ngrok-free.app/robot',
                'AUTH_USER_ID': 1,
                'NAME': 'Robot',
                'PROPERTIES': {
                    'bool': {
                        'Name': 'Да/Нет',
                        'Type': 'bool',
                        'Required': 'Y',
                        'Multiple': 'N'
                    },
                    'date': {
                        'Name': 'Дата',
                        'Type': 'date'
                    },
                    'datetime': {
                        'Name': 'Дата/Время',
                        'Type': 'datetime'
                    },
                    'double': {
                        'Name': 'Число',
                        'Type': 'double',
                        'Required': 'Y'
                    },
                    'int': {
                        'Name': 'Целое число',
                        'Type': 'int'
                    },
                    'select': {
                        'Name': 'Список',
                        'Type': 'select',
                        'Options': {
                            'one': 'one',
                                'two': 'two'
                        }
                    },
                    'string': {
                        'Name': 'Строка',
                        'Type': 'string',
                        'Default': 'default string value'
                    },
                    'text': {
                        'Name': 'Текст',
                        'Type': 'text'
                    },
                    'user': {
                        'Name': 'Пользователь',
                        'Type': 'user'
                    }
                }
            }
        ),
        client_endpoint=get_portal.endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result)


async def test_add_activity_todo(get_portal: PortalModel):
    result = await crest_auth.call(
        CallRequest(
            method="crm.activity.todo.add",
            params={
                'ownerTypeId': 2,
                'ownerId': 318,
                'title': 'ОБСУЖДАЕМ ПЛАНЫ',
                'description': 'Явка необязательна.',
                'deadline': datetime.now() + timedelta(hours=10),
                'responsibleId': 1,
                'settings': [
                    {
                        'link': 'example.com',
                        'id': 'link'
                    },
                    {
                        'from': 1724124440000,
                        'to': 1724124540000,
                        'duration': 1200000,
                        'location': '',
                        'selectedUserIds': [
                            1, 10
                        ],
                        'id': 'calendar'
                    },
                    {
                        'selectedClients': [
                            {
                                'entityId': 36469,
                                'entityTypeId': 3,
                                'isAvailable': True
                            },
                            {
                                'entityId': 2,
                                'entityTypeId': 4,
                                'isAvailable': True
                            }
                        ],
                        'id': 'client'
                    }
                ]
            }
        ),
        client_endpoint=get_portal.endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result)


async def test_get_contacts_from_deal(get_portal: PortalModel):
    """
    36465
    """
    result = await crest_auth.call(
        CallRequest(
            method="crm.deal.contact.items.get",
            params={
                'id': 318
            }
        ),
        client_endpoint=get_portal.endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result)


async def test_deal_get(get_portal: PortalModel):
    result = await crest_auth.call(
        CallRequest(
            method="crm.deal.get",
            params={
                'id': 318
            }
        ),
        client_endpoint=get_portal.endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token)
    )
    print(result)

async def test_contact_add_method_webhook():
    call_request = CallRequest(method="crm.contact.add", params={
                               "fields": {'name': 'pytest'}})
    for i in range(1):
        result = await crest_webhook.call(request=call_request)
        print(f"Method: '{call_request.method}'. Attempt # {
              i}. Result: {result}\n")


async def test_install_post(ac: AsyncClient, admin_refresh_token: str = '8fd9e66600704ff20070536200000001706207b51c5041ac22f9cb2585ae286730e85f'):
    result = await ac.post("/install", data={
        "REFRESH_ID": admin_refresh_token})
    print(result)


async def test_contact_add_method_auth_batch(get_portal: PortalModel):
    call_requests = [
        CallRequest(
            method="crm.contact.add",
            params={
                "fields": {'name': 'pytest_batch'}
            }
        )
        for i in range(7000)
    ]

    result = await crest_auth.call_batch(
        request_batch=call_requests,
        client_endpoint=get_portal.endpoint,
        auth_tokens=AuthTokens(
            access_token=get_portal.access_token, refresh_token=get_portal.refresh_token),
    )
    print(result)
    assert isinstance(result, list)

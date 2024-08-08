import asyncio
from crest.crest import CRestBitrix24, CallRequest
from config import *

client = CRestBitrix24(
    client_webhook=CLIENT_WEBHOOK,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)


async def call_test():
    params = {
        'FILTER': {
            '>DATE_CREATE': '2022-01-01'
        },
        'SELECT': [
            'NAME',
            'LAST_NAME',
            'EMAIL'
        ]
    }
    call_request = CallRequest(
        method="crm.contact.list",
        params=params
    )
    print(dict(call_request))
    print(
        await client.call(
            call_request
        )
    )


async def call_batch():
    cmd_batch = [
        CallRequest(
            method="crm.contact.list",
            params={
                'FILTER': {
                    '>DATE_CREATE': '2022-01-01'
                },
                'SELECT': [
                    'NAME',
                    'LAST_NAME',
                    'EMAIL'
                ]
            }
        ),
        CallRequest(
            method="crm.lead.add",
            params={
                'FILTER': {
                    '>DATE_CREATE': '2022-01-01'
                },
                'SELECT': [
                    'NAME',
                    'LAST_NAME',
                    'EMAIL'
                ]
            }
        )
    ]
    print(await client.call_batch(cmd_batch))

asyncio.run(call_test())

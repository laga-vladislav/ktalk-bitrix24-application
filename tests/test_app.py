import asyncio
from tests.conftest import crest_webhook
from crest.models import CallRequest


async def test_contact_add_method_webhook():
    call_request = CallRequest(method="crm.contact.add", params={
                               "fields": {'name': 'pytest'}})
    for i in range(2):
        result = await crest_webhook.call(request=call_request)
        print(f"Method: '{call_request.method}'. Attempt # {
              i}. Result: {result}\n")


async def test_contact_add_method_webhook_batch():
    call_requests = []
    # call_requests = [
    #     CallRequest(
    #         method="crm.contact.add",
    #         params={
    #             "fields": {
    #                 'name': f'pytest{i}'
    #             }
    #         }
    #     )
    #     for i in range(15)
    # ]
    for i in range(40):
        call_requests.append(
            CallRequest(
                method="crm.deal.add",
                params={
                    'fields':
                    {
                        "TITLE": f"Плановая продажа {i}",
                        "TYPE_ID": "GOODS",
                        "STAGE_ID": "NEW",
                        "COMPANY_ID": 3,
                        "CONTACT_ID": 3,
                        "OPENED": "Y",
                        "ASSIGNED_BY_ID": 1,
                        "PROBABILITY": 30,
                        "CURRENCY_ID": "USD",
                        "OPPORTUNITY": 5000,
                        "CATEGORY_ID": 5
                    }
                }
            )
        )
    result = await crest_webhook.call_batch(call_requests)
    # print(result)
asyncio.run(test_contact_add_method_webhook_batch())

# async def test_refresh_token():
#     vladsupermeowloveyouvlad = str
#     call_request = CallRequest(method="refresh_token")
#     for i in range(10):
#         crest_webhook.call()

import asyncio
import json
from crest.crest import CRestBitrix24, CallRequest

from environs import Env

env = Env()
env.read_env(override=True)

CLIENT_ID = env.str("CLIENT_ID", default=None)
CLIENT_SECRET = env.str("CLIENT_SECRET", default=None)
CLIENT_WEBHOOK = env.str("CLIENT_WEBHOOK", default=None)


CREST = CRestBitrix24(
    client_webhook=CLIENT_WEBHOOK, client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)


async def main():
    call_batches = []
    for i in range(1):
        call_batches.append(
            CallRequest(
                method="crm.contact.add", params={"fields": {"NAME": f"User{i}"}}
            )
        )

    result = await CREST.call_batch(call_batches)
    print(json.dumps(result, indent=4, ensure_ascii=False))

    call_request = CallRequest(method="crm.contact.list")
    result = await CREST.call(call_request)
    print(json.dumps(result, indent=4, ensure_ascii=False))


asyncio.run(main())

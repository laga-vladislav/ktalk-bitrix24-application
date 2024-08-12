from fastapi import APIRouter, Depends, Query

from crest.crest import CRestBitrix24
from crest.models import CallRequest
from src.router.utils import get_crest

router = APIRouter()

@router.get("/oauth_callback")
async def aouth_get_code(
    CRest: CRestBitrix24 = Depends(get_crest), code: str = Query(...)
):
    # можно брать code из middleware
    # code = request.state.query_params.get('code')
    result = await CRest.get_auth(code=code)
    parameters = {
        "filter": {"NAME": "User40"},
        "order": {"NAME": "DESC"},
    }
    callRequest = CallRequest(method="scope", params=parameters)

    result = await CRest.call(
        callRequest,
        access_token=result["access_token"],
        client_endpoint=result["client_endpoint"],
    )
    return result

    # call_batches = []
    # for i in range(200):
    #     call_batches.append(
    #         CallRequest(
    #             method="crm.contact.add", params={"fields": {"NAME": f"UserNew{i}"}}
    #         )
    #     )

    # result = await CRest.call_batch(
    #     call_batches,
    #     client_endpoint=result["client_endpoint"],
    #     access_token=result["access_token"],
    # )

    # return result

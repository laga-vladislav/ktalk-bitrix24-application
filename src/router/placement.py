from fastapi import APIRouter, Depends, Form, Request

from crest.crest import CRestBitrix24
from crest.models import AuthTokens, CallRequest
from src.router.utils import get_crest

router = APIRouter()


@router.post("/placement/crm_deal")
async def crm_deal(
    request: Request,
    CRest: CRestBitrix24 = Depends(get_crest),
    user_refresh_token: str = Form(..., alias="REFRESH_ID"),
    # user_access_token: str = Form(..., alias="AUTH_ID"),
):
    new_auth = await CRest.refresh_token(user_refresh_token)
    user_tokens = AuthTokens(
        access_token=new_auth["access_token"], refresh_token=new_auth["refresh_token"]
    )

    callreq = CallRequest(method="profile")
    result = await CRest.call(
        callreq, client_endpoint=new_auth["client_endpoint"], auth_tokens=user_tokens
    )

    return result

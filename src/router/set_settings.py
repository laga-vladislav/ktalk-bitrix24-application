from typing import AsyncGenerator

from fastapi import APIRouter, Body, Depends, Response

from crest.crest import CRestBitrix24
from src.db.database import get_session
from src.db.requests import get_portal
from src.router.utils import get_crest
from src.models import BitrixAppStorageModel
from src.bitrix_requests import set_options_bitrix_options

router = APIRouter()


@router.post("/set-settings")
async def handler(
    options: BitrixAppStorageModel,
    CRest: CRestBitrix24 = Depends(get_crest),
    session: AsyncGenerator = Depends(get_session),
):
    portal = await get_portal(session=session, member_id=options.member_id)

    await set_options_bitrix_options(CRest, portal, options)

    return Response(status_code=200)

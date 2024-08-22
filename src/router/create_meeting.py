from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from crest.crest import CRestBitrix24
from crest.models import AuthTokens, CallRequest
from src.router.utils import get_crest

router = APIRouter()


@router.post("/create_meeting")
async def handler(
    request: Request,
    CRest: CRestBitrix24 = Depends(get_crest),
):
    return

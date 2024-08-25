from fastapi import APIRouter, Depends, Form, Request, Query
from fastapi.responses import HTMLResponse

from crest.crest import CRestBitrix24
from src.router.utils import get_crest

from src.ktalk.requests import get_all_options_bitrix_options, create_meeting
from src.ktalk.models import MeetingModel, AppOptionModel
from pydantic import ValidationError

from src.logger.custom_logger import logger


router = APIRouter()


@router.post("/create_meeting")
async def handler(
    request: Request,
    creator_id: int,
    meeting: MeetingModel,
    CRest: CRestBitrix24 = Depends(get_crest)
):
    try:
        # TODO: как получить member_id? creator_id?
        app_options = await get_all_options_bitrix_options(
            crest_instance=CRest,
            portal=...
        )
        response = await create_meeting(
            meeting=meeting,
            app_options=app_options
        )
        return response
    except ValidationError as e:
        logger.error("Ошибка в формате параметра meeting")

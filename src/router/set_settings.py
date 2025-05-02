from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Response

from src.db.database import get_session
from src.db.requests import add_ktalk_space
from src.models import KtalkSpaceModel

router = APIRouter()


@router.post("/set-settings")
async def handler(
    ktalk_space: KtalkSpaceModel,
    session: AsyncGenerator = Depends(get_session),
):
    await add_ktalk_space(session=session, ktalk_space=ktalk_space)

    return Response(status_code=200)

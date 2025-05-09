from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Response, HTTPException

from src.db.database import get_session
from src.db.requests import get_portal, refresh_ktalk_space, get_ktalk_space, add_ktalk_space
from src.models import PortalModel, KtalkSpaceModel

router = APIRouter()


@router.post("/set-settings")
async def handler(
    ktalk_space: KtalkSpaceModel,
    session: AsyncGenerator = Depends(get_session),
):
    portal: PortalModel = await get_portal(
        session=session, member_id=ktalk_space.member_id
    )
    if not portal:
        return HTTPException(400, f"Портал {ktalk_space.member_id} не существует")
    
    current_ktalk_space: KtalkSpaceModel = await get_ktalk_space(
        session=session, portal=portal
    )
    if current_ktalk_space:
        await refresh_ktalk_space(
            session=session, ktalk_space=ktalk_space
        )
    else:
        await add_ktalk_space(
            session=session,ktalk_space=ktalk_space
        )

    return Response(status_code=200)

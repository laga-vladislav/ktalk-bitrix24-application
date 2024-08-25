from fastapi import Request
from crest.crest import CRestBitrix24
# from crest.models import AuthTokens
# from src.models import PortalModel
# from src.db.requests import get_portal as get_portal_db
# from sqlalchemy.ext.asyncio import AsyncSession


def get_crest(request: Request) -> CRestBitrix24:
    return request.app.state.CRest


# async def get_portal(request: Request, session: AsyncSession, member_id: str, tokens: AuthTokens) -> PortalModel:
#     crest = get_crest(request)
#     # auth = await crest.refresh_token(refresh_token='0945ea660070836a00705362000000017062070b2734dbeda74dfd66c5e5846d3bec79')
#     portal = get_portal_db(
#         session=session,
#         member_id=member_id
#     )
#     if not portal:
#         portal = await crest.refresh_token()

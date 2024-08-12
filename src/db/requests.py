from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.schemes import *
from src.db.models import *


async def get_portal(session: AsyncSession, member_id: str) -> PortalModel:
    res = await session.execute(select(PortalScheme).where(PortalScheme.member_id == member_id))
    res = res.scalars()
    portal_model = PortalModel.model_validate(res)
    return portal_model


async def add_portal(session: AsyncSession, portal_model: PortalModel):
    pass

from typing import AsyncGenerator
from src.db.models import PortalModel
from src.db.schemes import PortalScheme
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.logger.custom_logger import logger


async def add_portal(session: AsyncSession, portal: PortalModel | dict) -> None:
    try:
        session.add(PortalScheme(**dict(portal)))
        await session.commit()
    except IntegrityError:
        logger.error(f"Портал с member_id '{
                     portal['member_id']}' уже существует")


async def get_portal(session: AsyncSession, member_id: str) -> PortalModel | None:
    result = await session.execute(select(PortalScheme).where(PortalScheme.member_id == member_id))
    portal_scheme = result.scalar()
    if portal_scheme:
        return PortalModel(**portal_scheme.__dict__)
    return None
    # код ниже вызывает ошибку, связанную с тем, что одновременно у sqlite может быть только одно соединение (втф)
    # return PortalModel(**result.scalar().__dict__) if result.scalar() else None


async def refresh_portal(session: AsyncSession, portal: PortalModel) -> None:
    await session.execute(update(PortalScheme).where(PortalScheme.member_id == portal.member_id).values(**dict(portal)))
    await session.commit()

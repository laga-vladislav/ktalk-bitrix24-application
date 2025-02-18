from src.models import PortalModel, UserModel
from src.db.schemes import PortalScheme, UserScheme
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.logger.custom_logger import logger


async def add_user(session: AsyncSession, user: UserModel) -> None:
    try:
        session.add(UserScheme(**user.model_dump()))
        await session.commit()
    except IntegrityError:
        logger.info(
            f"Пользователь {user} уже существует. Запуск обновления"
        )
        await session.rollback()  # Сбрасываем состояние транзакции
        await refresh_user(session, user)


async def refresh_user(session: AsyncSession, user: UserModel) -> None:
    try:
        stmt = (
            update(UserScheme).where(UserScheme.id == user.id,
                                     UserScheme.member_id == user.member_id).values(**user.model_dump())
        )
        await session.execute(statement=stmt)
        await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при обновлении пользователя: {e}")
        await session.rollback()  # Сбрасываем состояние транзакции в случае ошибки


async def get_user(session: AsyncSession, id: int, member_id: str) -> UserModel:
    try:
        result = await session.execute(select(UserScheme).where(and_(UserScheme.id == id, UserScheme.member_id == member_id)))
        user_scheme = result.scalar()
        if user_scheme:
            return UserModel(**user_scheme.__dict__)
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя: {e}")


async def add_portal(session: AsyncSession, portal: PortalModel | dict) -> None:
    """
    Добавить портал в базу данных
    """
    try:
        session.add(PortalScheme(**portal.model_dump()))
        await session.commit()
    except IntegrityError:
        logger.error(f"Портал с member_id '{
                     portal['member_id']}' уже существует")


async def get_portal(session: AsyncSession, member_id: str) -> PortalModel | None:
    """
    Получить портал из базы данных, либо None, если его нет
    """
    result = await session.execute(select(PortalScheme).where(PortalScheme.member_id == member_id))
    portal_scheme = result.scalar()
    if portal_scheme:
        return PortalModel(**portal_scheme.__dict__)
    return None
    # код ниже вызывает ошибку, связанную с тем, что одновременно у sqlite может быть только одно соединение (втф)
    # return PortalModel(**result.scalar().__dict__) if result.scalar() else None


async def refresh_portal(session: AsyncSession, portal: PortalModel) -> None:
    """
    Обновить данные портала в базе данных
    """
    await session.execute(update(PortalScheme).where(PortalScheme.member_id == portal.member_id).values(**portal.model_dump()))
    await session.commit()

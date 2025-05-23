from src.models import PortalModel, UserModel, UserAuthModel, KtalkSpaceModel
from src.db.schemes import PortalScheme, UserScheme, UserAuthScheme, KtalkSpaceScheme
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.logger.custom_logger import logger


async def add_portal(session: AsyncSession, portal: PortalModel) -> None:
    """
    Добавить портал в базу данных
    """
    try:
        session.add(PortalScheme(**portal.model_dump()))
        await session.commit()
    except IntegrityError:
        logger.error(f"Портал с member_id '{portal['member_id']}' уже существует")
        raise


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


async def add_ktalk_space(session: AsyncSession, ktalk_space: KtalkSpaceModel):
    try:
        session.add(KtalkSpaceScheme(**ktalk_space.model_dump()))
        await session.commit()
    except IntegrityError as e:
        logger.error(f"Ошибка при добавлении пространства КТолк: {e}")
        raise


async def get_ktalk_space(session: AsyncSession, portal: PortalModel) -> KtalkSpaceModel | None:
    try:
        result = await session.execute(select(KtalkSpaceScheme).where(
            KtalkSpaceScheme.member_id == portal.member_id
        ))
        ktalk_space = result.scalar()
        if ktalk_space:
            return KtalkSpaceModel(**ktalk_space.__dict__)
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении пространства КТолк: {e}")
        raise


async def refresh_ktalk_space(session: AsyncSession, ktalk_space: KtalkSpaceModel):
    try:
        stmt = (
            update(KtalkSpaceScheme).where(KtalkSpaceScheme.member_id == ktalk_space.member_id).values(
                **ktalk_space.model_dump()
            )
        )
        await session.execute(statement=stmt)
        await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при обновлении пространства КТолк: {e}")
        await session.rollback()
        raise


async def add_user(session: AsyncSession, user: UserModel) -> None:
    try:
        session.add(UserScheme(**user.model_dump()))
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        error_msg = str(e.orig)

        if "UNIQUE constraint failed" in error_msg or "PRIMARY KEY constraint failed" in error_msg:
            logger.info(
                f"Пользователь {user} уже существует. Запуск обновления"
            )
            await refresh_user(session, user)
        elif "FOREIGN KEY constraint failed" in error_msg:
            raise 
        else:
            raise 


async def refresh_user(session: AsyncSession, user: UserModel) -> None:
    try:
        stmt = (
            update(UserScheme).where(UserScheme.user_id == user.user_id,
                                     UserScheme.member_id == user.member_id).values(**user.model_dump())
        )
        await session.execute(statement=stmt)
        await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при обновлении пользователя: {e}")
        await session.rollback()  # Сбрасываем состояние транзакции в случае ошибки
        raise


async def get_user(session: AsyncSession, user_id: int, member_id: str) -> UserModel | None:
    try:
        result = await session.execute(select(UserScheme).where(and_(UserScheme.user_id == user_id, UserScheme.member_id == member_id)))
        user_scheme = result.scalar()
        if user_scheme:
            return UserModel(**user_scheme.__dict__)
            # return UserModel.model_validate(user_scheme)
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя: {e}")
        raise


async def set_user_auth(session: AsyncSession, auth: UserAuthModel):
    """
    Основной метод для работы с авторизацией.
    При отсутствии данных авторизации - добавляет в базу данных,
    При наличии данных - обновляет
    """
    try:
        existing = await get_user_auth(session, UserModel(user_id=auth.user_id, member_id=auth.member_id, name="", last_name="", is_admin=False))
        if existing:
            await _refresh_user_auth(session, auth)
        else:
            await _add_user_auth(session, auth)
    except Exception as e:
        logger.error(f"Ошибка при установке токена пользователя: {e}")
        raise

async def _add_user_auth(session: AsyncSession, auth: UserAuthModel):
    try:
        session.add(UserAuthScheme(**auth.model_dump()))
        await session.commit()
    except IntegrityError as e:
        logger.error(f"Ошибка при добавлении данных авторизации пользователя: {e}")
        await session.rollback()
        raise

async def get_user_auth(session: AsyncSession, user: UserModel) -> UserAuthModel | None:
    try:
        result = await session.execute(
            select(UserAuthScheme)
            .options(joinedload(UserAuthScheme.portal))  # Подгружаем portal
            .where(
                and_(
                    UserAuthScheme.user_id == user.user_id,
                    UserAuthScheme.member_id == user.member_id
                )
            )
        )
        user_token_scheme = result.scalars().first()
        if user_token_scheme:
            return UserAuthModel(**user_token_scheme.to_dict())
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении данных авторизации пользователя: {e}")
        raise

async def get_user_auth_without_model(session: AsyncSession, member_id: str, user_id: str) -> UserAuthModel | None:
    temp_user_model = UserModel(
        member_id=member_id,
        user_id=user_id,
        name="",
        last_name="",
        is_admin=False
    )
    return await get_user_auth(session=session, user=temp_user_model)    

async def _refresh_user_auth(session: AsyncSession, auth: UserAuthModel):
    try:
        stmt = (
            update(UserAuthScheme).where(UserAuthScheme.user_id == auth.user_id,
                                          UserAuthScheme.member_id == auth.member_id).values(
                                              **auth.model_dump()
                                          )
        )
        await session.execute(statement=stmt)
        await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при обновлении токена пользователя: {e}")
        await session.rollback()
        raise

async def _delete_user_auth(session: AsyncSession, auth: UserAuthModel):
    try:
        await session.execute(delete(UserAuthScheme).where(UserAuthScheme.user_id == auth.user_id,
                                                            UserAuthScheme.member_id == auth.member_id))
        await session.commit()        
    except Exception as e:
        logger.error(f"Ошибка при удалении токеа пользователя: {e}")
        await session.rollback()
        raise

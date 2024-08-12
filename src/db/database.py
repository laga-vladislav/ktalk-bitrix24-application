from sqlalchemy import BigInteger, String
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import os

engine = create_async_engine(url=os.getenv("DATABASE_URI"))
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Portal(Base):
    __tablename__ = "portal"

    member_id: Mapped[str] = mapped_column(primary_key=True)
    endpoint: Mapped[str] = mapped_column()
    scope: Mapped[str] = mapped_column()



async def db_run():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
import os
from typing import AsyncGenerator

from src.db.schemes import Base

from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


engine = create_async_engine(url=os.getenv("DATABASE_URI"), echo=False)
session_factory = async_sessionmaker(autocommit=False, bind=engine)

@event.listens_for(engine.sync_engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('pragma foreign_keys=ON')
    cursor.close()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


async def run_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

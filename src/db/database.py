import os
from dotenv import load_dotenv
from typing import AsyncGenerator

from src.db.schemes import Base

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

load_dotenv()

engine = create_async_engine(url=os.getenv("DATABASE_URI"), echo=False)
session_factory = async_sessionmaker(autocommit=False, bind=engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


async def run_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


engine = create_async_engine(
    url=os.getenv("DATABASE_URI"),
    echo=True
)
async_session = async_sessionmaker(engine)

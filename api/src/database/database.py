from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config.database_config import DatabaseConfig


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, database_config: DatabaseConfig = DatabaseConfig()):
        self.engine = create_async_engine(database_config.url_connection)
        self._Session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._Session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


db = Database()


async def get_main_session() -> AsyncGenerator[AsyncSession, None]:
    async with db.get_session() as session:
        yield session

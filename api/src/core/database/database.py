"""Motor async de SQLAlchemy y manejo de sesión con rollback/close a prueba de
fallos."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.exc import DBAPIError, InterfaceError, InternalError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from core.config.database_config import db_config
from core.config.logger import logger


def _is_terminated_connection_error(exc: DBAPIError) -> bool:
    """True si el fallo se debe a que la conexión ya no es usable
    (terminada/invalidada).

    Ocurre en el apagado: uvicorn cierra los WebSocket cuyo ``get_main_session``
    mantiene una transacción viva, y el ``commit`` de teardown corre sobre una
    conexión asyncpg a mitad de una operación cancelada (``another operation is in
    progress``). No es un fallo lógico de datos, así que se descarta en lugar de
    propagarlo por el stack ASGI. Un error real de commit (p. ej. IntegrityError) NO
    invalida la conexión y sí se re-lanza.
    """
    return getattr(exc, "connection_invalidated", False) or isinstance(
        exc, (InterfaceError, InternalError)
    )


# Sin esto, Postgres nombra solo cualquier constraint que el modelo no bautice a mano
# (`documentos_pkey`, `usuarios_clave_objeto_key`, …) y Alembic no puede
# referenciarla: los downgrade quedan con nombres adivinados y un cambio de
# constraint no se detecta en el autogenerate. Con la convención, el nombre lo decide
# el modelo y es el mismo en la base, en la migración y en el metadata. Un `name=`
# explícito en el modelo siempre gana.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Database:
    def __init__(self, database_config=db_config):
        self.engine = create_async_engine(
            database_config.url_connection,
            pool_size=8,
            max_overflow=8,
            pool_recycle=3600,
            connect_args={"timeout": 10},
        )
        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_factory() as session:
            try:
                yield session
                try:
                    await session.commit()
                except DBAPIError as exc:
                    # Apagado: si la conexión ya está terminada, descartar en
                    # silencio; cualquier otro fallo de commit se propaga como
                    # siempre.
                    if not _is_terminated_connection_error(exc):
                        raise
                    logger.warning(
                        "[db] commit descartado: conexión terminada durante el cierre"
                    )
                    await self._safe_rollback(session)
            except Exception:
                await self._safe_rollback(session)
                raise
            finally:
                await self._safe_close(session)

    @staticmethod
    async def _safe_rollback(session: AsyncSession) -> None:
        try:
            await session.rollback()
        except DBAPIError:
            # La conexión ya no responde (cierre); nada que revertir.
            pass

    @staticmethod
    async def _safe_close(session: AsyncSession) -> None:
        try:
            await session.close()
        except DBAPIError:
            pass


db = Database()


async def get_main_session() -> AsyncGenerator[AsyncSession, None]:
    async with db.get_session() as session:
        yield session

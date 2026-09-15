import asyncio
import os
import sys

from dotenv import load_dotenv
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Alembic no compara los ENUM nativos de Postgres: agregar un miembro a un enum de Python
# produce un diff vacío y el fallo aparece recién en runtime, al insertar el valor nuevo
# (InvalidTextRepresentation). Importar este módulo registra los comparadores que faltan,
# y el autogenerate pasa a emitir solo el ALTER TYPE ... ADD VALUE — con su
# autocommit_block(), porque Postgres no lo admite dentro de la transacción de la
# migración. También detecta valores eliminados y renombres de tipo.
import alembic_postgresql_enum  # noqa: F401

# Añadir src/ al path para que los imports de los modelos funcionen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

load_dotenv()

from core.config.database_config import db_config  # noqa: E402

# import core.config.models registra todos los modelos en Base.metadata para que Alembic los detecte
import core.config.models  # noqa: E402, F401
from core.database.database import Base  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def migration_url() -> str:
    """URL de conexión para migrar — Postgres directo, no pgbouncer.

    La API habla con la base a través de pgbouncer en modo `transaction`, donde el pooler
    devuelve la conexión al pool al cerrar cada transacción. Ahí las migraciones no
    funcionan: `CREATE INDEX CONCURRENTLY` y cualquier `autocommit_block()` necesitan una
    sesión propia y estable. ALEMBIC_DB_HOST/ALEMBIC_DB_PORT apuntan al Postgres real; si
    no están definidas se usa la conexión normal de la app.
    """
    host = os.getenv("ALEMBIC_DB_HOST") or db_config.host
    port = os.getenv("ALEMBIC_DB_PORT") or db_config.port
    return (
        f"{db_config.database_engine}+{db_config.database_driver}://"
        f"{db_config.username}:{db_config.password}@{host}:{port}/{db_config.database_name}"
    )


def _skip_empty_revision(context_, revision, directives) -> None:
    """Evita revisiones vacías cuando `--autogenerate` no encontró nada que cambiar.

    Sin esto, un autogenerate sin cambios genera igual un archivo con `pass` en upgrade y
    downgrade, y esos archivos se acumulan en la historia sin decir nada.
    """
    if getattr(context_.config.cmd_opts, "autogenerate", False) and directives[0].upgrade_ops.is_empty():
        directives[:] = []
        print("Sin cambios en los modelos: no se genera revisión.")


# compare_type: detecta cambios de tipo de columna (p. ej. Double -> Numeric).
# compare_server_default: detecta cambios de DEFAULT del lado de Postgres. Ojo, ninguno
# de los dos ve renombres — un rename siempre se autogenera como drop + add, y eso
# borra datos: hay que reescribirlo a mano como `op.alter_column(..., new_column_name=)`.
_CONTEXT_OPTS = dict(
    target_metadata=target_metadata,
    compare_type=True,
    compare_server_default=True,
    process_revision_directives=_skip_empty_revision,
)


def run_migrations_offline() -> None:
    context.configure(
        url=migration_url(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **_CONTEXT_OPTS,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, **_CONTEXT_OPTS)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(migration_url())
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

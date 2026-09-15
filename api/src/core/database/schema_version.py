from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection
from sqlalchemy.exc import SQLAlchemyError

from core.config.logger import logger
from core.database.database import db

# El esquema lo crean las migraciones de Alembic, no la app (antes: Base.metadata.create_all
# en el arranque). Esta verificación compara la base contra la última revisión y ADVIERTE
# si no coinciden — a propósito no aborta el arranque.
#
# Es una decisión consciente, no un descuido: el flujo elegido para generar y aplicar la
# migración inicial es entrar al contenedor ya corriendo (`podman compose exec api sh` ->
# `alembic revision --autogenerate` -> `alembic upgrade head`), y eso requiere que el
# contenedor se quede arriba con la base todavía sin migrar. Si esto abortara el arranque
# como antes, uvicorn nunca llegaría a aceptar conexiones, el `restart: unless-stopped` de
# compose reiniciaría el contenedor en bucle, y `exec` no tendría a qué entrar (ver el
# 137/SIGKILL de cuando esto sí abortaba). El costo de la advertencia: la app queda arriba
# en un estado degradado hasta migrar — los seeds y los contadores diarios del lifespan
# (ver lifespan.py) también van a fallar y solo advertir, y cualquier endpoint que toque
# una tabla que todavía no existe va a devolver 500 hasta correr `alembic upgrade head`.
_ALEMBIC_ROOT = Path(__file__).resolve().parents[3]


def _alembic_config() -> Config:
    config = Config(str(_ALEMBIC_ROOT / "alembic.ini"))
    # script_location en el .ini es relativo ("alembic") y Alembic lo resolvería contra el
    # cwd del proceso. Uvicorn no garantiza cuál es, así que se fija absoluto.
    config.set_main_option("script_location", str(_ALEMBIC_ROOT / "alembic"))
    return config


def _current_revision(connection: Connection) -> str | None:
    return MigrationContext.configure(connection).get_current_revision()


async def verify_schema_is_current() -> None:
    """Advierte si la base no está migrada hasta la última revisión. No aborta el arranque."""
    try:
        head = ScriptDirectory.from_config(_alembic_config()).get_current_head()
        if head is None:
            logger.warning(
                "[schema] no hay ninguna revisión en alembic/versions todavía: el esquema "
                "no existe. Generarla con `alembic revision --autogenerate -m \"...\"` y "
                "aplicarla con `alembic upgrade head`."
            )
            return

        async with db.engine.connect() as connection:
            current = await connection.run_sync(_current_revision)

        if current == head:
            return

        detalle = (
            "la base no tiene ninguna migración aplicada"
            if current is None
            else f"la base está en la revisión {current}"
        )
        logger.warning(
            f"[schema] desactualizado: {detalle} y la última es {head}. "
            "Corre `alembic upgrade head` — hasta entonces la app queda en un estado "
            "degradado (seeds y endpoints sobre tablas faltantes van a fallar)."
        )
    except SQLAlchemyError as exc:
        # P.ej. la base todavía no acepta conexiones, o el usuario/DB no existen. Se
        # advierte por la misma razón que arriba: no cortar el arranque.
        logger.warning(f"[schema] no se pudo comparar la revisión de la base: {exc}")

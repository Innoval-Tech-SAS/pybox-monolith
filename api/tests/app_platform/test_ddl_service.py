"""Tests de `DdlService` sin pasar por HTTP: cubre las 4 acciones de `alter_table`
(ADD/DROP/MODIFY/RENAME_COLUMN) y el rechazo de identificadores inválidos.

Corre contra la propia base de datos de test (`db_config.database_name`, ver
`conftest.py`), con su propia conexión fuera de la transacción de `db_session` --
igual que `test_database_controller.py::TestCreateTable`/`TestAlterTable`. No hace
falta limpieza: el esquema se recrea completo en la próxima sesión de pytest.
"""

import uuid

import pytest
from sqlalchemy import text

from app_platform.schema_manager.schemas.database_schemas import (
    AlterAction,
    ColumnDataType,
    ColumnDefinition,
)
from app_platform.schema_manager.services.ddl_service import DdlService
from core.config.database_config import db_config


def _table_name() -> str:
    return f"test_ddl_svc_{uuid.uuid4().hex}"


@pytest.fixture
async def real_table():
    service = DdlService()
    table_name = _table_name()
    result = await service.create_table(
        db_config.database_name,
        "public",
        table_name,
        [ColumnDefinition(name="id", data_type=ColumnDataType.INTEGER)],
    )
    assert result["success"] is True
    return table_name


class TestCreateTable:
    async def test_valid_with_multiple_column_kinds(self):
        service = DdlService()
        table_name = _table_name()
        result = await service.create_table(
            db_config.database_name,
            "public",
            table_name,
            [
                ColumnDefinition(
                    name="id",
                    data_type=ColumnDataType.INTEGER,
                    primary_key=True,
                    nullable=False,
                ),
                ColumnDefinition(
                    name="etiqueta", data_type=ColumnDataType.VARCHAR, length=50
                ),
                ColumnDefinition(
                    name="monto",
                    data_type=ColumnDataType.NUMERIC,
                    precision=10,
                    scale=2,
                ),
                ColumnDefinition(
                    name="activo",
                    data_type=ColumnDataType.BOOLEAN,
                    default_value="true",
                ),
            ],
        )
        assert result["success"] is True

    async def test_no_columns_returns_failure_without_touching_db(self):
        service = DdlService()
        result = await service.create_table(
            db_config.database_name, "public", _table_name(), []
        )
        assert result["success"] is False
        assert "columna" in result["message"]

    async def test_invalid_database_name_rejected(self):
        service = DdlService()
        result = await service.create_table(
            "not a valid db!",
            "public",
            _table_name(),
            [ColumnDefinition(name="id", data_type=ColumnDataType.INTEGER)],
        )
        assert result["success"] is False
        assert "Identificador inválido" in result["message"]


class TestAlterTableAddColumn:
    async def test_valid(self, real_table, db_session):
        service = DdlService()
        result = await service.alter_table(
            db_config.database_name,
            "public",
            real_table,
            AlterAction.ADD_COLUMN,
            ColumnDefinition(name="extra", data_type=ColumnDataType.TEXT),
            None,
            None,
        )
        assert result["success"] is True
        cols = (
            (
                await db_session.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns WHERE table_name = :t"
                    ),
                    {"t": real_table},
                )
            )
            .scalars()
            .all()
        )
        assert "extra" in cols

    async def test_missing_column_definition_fails(self, real_table):
        service = DdlService()
        result = await service.alter_table(
            db_config.database_name,
            "public",
            real_table,
            AlterAction.ADD_COLUMN,
            None,
            None,
            None,
        )
        assert result["success"] is False


class TestAlterTableDropColumn:
    async def test_valid(self, real_table, db_session):
        service = DdlService()
        await service.alter_table(
            db_config.database_name,
            "public",
            real_table,
            AlterAction.ADD_COLUMN,
            ColumnDefinition(name="temporal", data_type=ColumnDataType.TEXT),
            None,
            None,
        )
        result = await service.alter_table(
            db_config.database_name,
            "public",
            real_table,
            AlterAction.DROP_COLUMN,
            None,
            "temporal",
            None,
        )
        assert result["success"] is True
        cols = (
            (
                await db_session.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns WHERE table_name = :t"
                    ),
                    {"t": real_table},
                )
            )
            .scalars()
            .all()
        )
        assert "temporal" not in cols

    async def test_missing_column_name_fails(self, real_table):
        service = DdlService()
        result = await service.alter_table(
            db_config.database_name,
            "public",
            real_table,
            AlterAction.DROP_COLUMN,
            None,
            None,
            None,
        )
        assert result["success"] is False


class TestAlterTableModifyColumn:
    async def test_valid_changes_type_and_nullability(self, real_table, db_session):
        service = DdlService()
        await service.alter_table(
            db_config.database_name,
            "public",
            real_table,
            AlterAction.ADD_COLUMN,
            ColumnDefinition(name="edad", data_type=ColumnDataType.TEXT),
            None,
            None,
        )
        # Necesita valores castables a INTEGER para que el USING no falle en filas
        # existentes -- la tabla está vacía, así que no hay filas que romper.
        result = await service.alter_table(
            db_config.database_name,
            "public",
            real_table,
            AlterAction.MODIFY_COLUMN,
            ColumnDefinition(
                name="edad", data_type=ColumnDataType.INTEGER, nullable=False
            ),
            "edad",
            None,
        )
        assert result["success"] is True
        row = (
            await db_session.execute(
                text(
                    "SELECT data_type, is_nullable FROM information_schema.columns WHERE table_name = :t AND column_name = 'edad'"
                ),
                {"t": real_table},
            )
        ).first()
        assert row.data_type == "integer"
        assert row.is_nullable == "NO"

    async def test_missing_column_name_fails(self, real_table):
        service = DdlService()
        result = await service.alter_table(
            db_config.database_name,
            "public",
            real_table,
            AlterAction.MODIFY_COLUMN,
            ColumnDefinition(name="x", data_type=ColumnDataType.TEXT),
            None,
            None,
        )
        assert result["success"] is False

    async def test_missing_column_definition_fails(self, real_table):
        service = DdlService()
        result = await service.alter_table(
            db_config.database_name,
            "public",
            real_table,
            AlterAction.MODIFY_COLUMN,
            None,
            "id",
            None,
        )
        assert result["success"] is False


class TestAlterTableRenameColumn:
    async def test_valid(self, real_table, db_session):
        service = DdlService()
        result = await service.alter_table(
            db_config.database_name,
            "public",
            real_table,
            AlterAction.RENAME_COLUMN,
            None,
            "id",
            "identificador",
        )
        assert result["success"] is True
        cols = (
            (
                await db_session.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns WHERE table_name = :t"
                    ),
                    {"t": real_table},
                )
            )
            .scalars()
            .all()
        )
        assert "identificador" in cols
        assert "id" not in cols

    async def test_missing_new_name_fails(self, real_table):
        service = DdlService()
        result = await service.alter_table(
            db_config.database_name,
            "public",
            real_table,
            AlterAction.RENAME_COLUMN,
            None,
            "id",
            None,
        )
        assert result["success"] is False


class TestAlterTableInvalidIdentifiers:
    async def test_invalid_table_name_rejected(self):
        service = DdlService()
        result = await service.alter_table(
            db_config.database_name,
            "public",
            "not a valid table!",
            AlterAction.DROP_COLUMN,
            None,
            "id",
            None,
        )
        assert result["success"] is False
        assert "Identificador inválido" in result["message"]

    async def test_invalid_column_name_in_drop_rejected(self, real_table):
        service = DdlService()
        result = await service.alter_table(
            db_config.database_name,
            "public",
            real_table,
            AlterAction.DROP_COLUMN,
            None,
            "bad col!",
            None,
        )
        assert result["success"] is False
        assert "Identificador inválido" in result["message"]

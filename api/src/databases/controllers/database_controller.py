from fastapi import HTTPException, status

from config.api_router import APIRouter
from databases.dependencies import DdlServiceDep, DmlServiceDep, InspectorServiceDep
from databases.schemas.database_schemas import (
    AlterTableRequest,
    CreateDatabaseRequest,
    CreateTableRequest,
    DynamicQueryRequest,
    DynamicQueryResponse,
    FieldInfo,
    OperationResponse,
)
from security.dependencies import CurrentSession
from users.schemas.user_session_schema import UserSession

router = APIRouter(prefix="/databases", tags=["Bases de datos"])


def _require_global(session: UserSession) -> None:
    if not session.is_global:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo usuarios globales pueden realizar esta acción")


def _require_org_or_global(session: UserSession) -> None:
    if not session.is_global and not session.orgs:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso")


# ------------------------------------------------------------------
# Inspección (org + global)
# ------------------------------------------------------------------

@router.get("/schemas", response_model=list[str], summary="Listar esquemas")
async def list_schemas(session: CurrentSession, service: InspectorServiceDep) -> list[str]:
    _require_org_or_global(session)
    return await service.get_schemas()


@router.get("/schemas/{schema_name}/tables", response_model=list[str], summary="Listar tablas de un esquema")
async def list_tables(
    schema_name: str,
    session: CurrentSession,
    service: InspectorServiceDep,
) -> list[str]:
    _require_org_or_global(session)
    return await service.get_tables(schema_name)


@router.get(
    "/schemas/{schema_name}/tables/{table_name}/fields",
    response_model=list[FieldInfo],
    summary="Listar campos de una tabla",
)
async def list_table_fields(
    schema_name: str,
    table_name: str,
    session: CurrentSession,
    service: InspectorServiceDep,
) -> list[FieldInfo]:
    _require_org_or_global(session)
    raw = await service.get_table_fields(schema_name, table_name)
    return [FieldInfo(name=col["name"], type=str(col["type"])) for col in raw]


# ------------------------------------------------------------------
# Consulta dinámica (org + global)
# ------------------------------------------------------------------

@router.post("/query", response_model=DynamicQueryResponse, summary="Ejecutar consulta dinámica")
async def execute_query(
    body: DynamicQueryRequest,
    session: CurrentSession,
    service: DmlServiceDep,
) -> DynamicQueryResponse:
    _require_org_or_global(session)
    result = await service.execute_query(
        tables=[t.model_dump() for t in body.tables],
        joins=[j.model_dump() for j in body.joins],
        limit=body.limit,
        query_mode=body.query_mode,
        group_by=[g.model_dump() for g in body.group_by],
        aggregations=[a.model_dump() for a in body.aggregations],
        having=[h.model_dump() for h in body.having],
        order_by=[o.model_dump() for o in body.order_by],
    )
    return DynamicQueryResponse(**result)


# ------------------------------------------------------------------
# DDL (global only)
# ------------------------------------------------------------------

@router.post("/", response_model=OperationResponse, status_code=status.HTTP_201_CREATED, summary="Crear base de datos")
async def create_database(
    body: CreateDatabaseRequest,
    session: CurrentSession,
    service: DdlServiceDep,
) -> OperationResponse:
    _require_global(session)
    result = await service.create_database(body.database_name)
    return OperationResponse(**result)


@router.post(
    "/{database_name}/schemas/{schema_name}/tables",
    response_model=OperationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear tabla",
)
async def create_table(
    database_name: str,
    schema_name: str,
    body: CreateTableRequest,
    session: CurrentSession,
    service: DdlServiceDep,
) -> OperationResponse:
    _require_global(session)
    result = await service.create_table(database_name, schema_name, body.table_name, body.columns)
    return OperationResponse(**result)


@router.patch(
    "/{database_name}/schemas/{schema_name}/tables/{table_name}",
    response_model=OperationResponse,
    summary="Alterar tabla",
)
async def alter_table(
    database_name: str,
    schema_name: str,
    table_name: str,
    body: AlterTableRequest,
    session: CurrentSession,
    service: DdlServiceDep,
) -> OperationResponse:
    _require_global(session)
    result = await service.alter_table(
        database_name,
        schema_name,
        table_name,
        body.action,
        body.column,
        body.column_name,
        body.new_column_name,
    )
    return OperationResponse(**result)

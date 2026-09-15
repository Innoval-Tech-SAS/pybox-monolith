from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from receivables.credits.dependencies import CreditCatalogServiceDep
from receivables.credits.schemas.credit_catalog_schemas import CreditTypeOption

router = APIRouter(prefix="/credits", tags=["Catálogos de créditos"])


@router.get(
    "/types",
    response_model=list[CreditTypeOption],
    summary="Listar tipos de crédito",
    description="Catálogo código→etiqueta de tipos de crédito, para los selects y etiquetas del front. "
    "Reemplaza el dict estático que el frontend mantenía por su cuenta.",
)
async def list_credit_types(
    _: CurrentSession,
    service: CreditCatalogServiceDep,
) -> list[CreditTypeOption]:
    return service.list_credit_types()

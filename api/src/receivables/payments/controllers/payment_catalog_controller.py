"""Endpoint de catálogo de estados de pago."""

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from receivables.payments.dependencies import PaymentCatalogServiceDep
from receivables.payments.schemas.payment_catalog_schemas import PaymentStatusOption

router = APIRouter(prefix="/payments", tags=["Catálogos de pagos"])


@router.get(
    "/statuses",
    response_model=list[PaymentStatusOption],
    summary="Listar estados de pago",
    description=(
        "Catálogo código→etiqueta de estados de cuota, para los chips y filtros "
        "del front."
    ),
)
async def list_statuses(
    _: CurrentSession,
    service: PaymentCatalogServiceDep,
) -> list[PaymentStatusOption]:
    return service.list_statuses()

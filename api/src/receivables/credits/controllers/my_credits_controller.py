from core.config.api_router import APIRouter
from receivables.credits.dependencies import MyCreditsServiceDep
from receivables.credits.schemas.my_credits_schemas import CreditWithPayments
from core.security.dependencies import CurrentSession
from core.security.policies import get_self_identity

router = APIRouter(prefix="/credits", tags=["Mis Créditos"])


@router.get(
    "/my-credits",
    response_model=list[CreditWithPayments],
    summary="Consultar mis créditos",
    description="Retorna los créditos del deudor autenticado, incluyendo pagos y saldo por crédito.",
)
async def my_credits(
    session: CurrentSession,
    service: MyCreditsServiceDep,
) -> list[CreditWithPayments]:
    doc_type, doc_number = get_self_identity(session)
    return await service.get_my_credits(doc_type, doc_number)

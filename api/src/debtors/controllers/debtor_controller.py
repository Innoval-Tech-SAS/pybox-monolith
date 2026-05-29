import uuid
from typing import Annotated

from fastapi import Query, status

from config.api_router import APIRouter
from debtors.dependencies import DebtorServiceDep
from debtors.schemas.debtor_schemas import (
    AddressResponse,
    ContactMethodResponse,
    CreateAddressRequest,
    CreateContactMethodRequest,
    CreateDebtorRequest,
    DebtorCreditResponse,
    DebtorDetailResponse,
    DebtorListResponse,
    DebtorResponse,
    RelatedContactsResponse,
)
from security.dependencies import CurrentSession

from config.logger import logger

router = APIRouter(prefix="/debtors", tags=["Deudores"])


@router.get(
    "/",
    response_model=DebtorListResponse,
    summary="Listar deudores",
    description="Lista paginada de deudores. Requiere `portfolioId` para usuarios no globales.",
)
async def list_debtors(
    session: CurrentSession,
    service: DebtorServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    document_number: Annotated[str | None, Query(alias="documentNumber")] = None,
    portfolio_id: Annotated[uuid.UUID | None, Query(alias="portfolioId")] = None,
) -> DebtorListResponse:
    return await service.list_debtors(
        user_session=session,
        page=page,
        page_size=page_size,
        document_number=document_number,
        portfolio_id=portfolio_id,
    )


@router.get(
    "/{debtor_id}",
    response_model=DebtorDetailResponse,
    summary="Obtener deudor por ID",
    description="Retorna el deudor con sus direcciones y métodos de contacto.",
)
async def get_debtor(
    debtor_id: int,
    session: CurrentSession,
    service: DebtorServiceDep,
    portfolio_id: Annotated[uuid.UUID | None, Query(alias="portfolioId")] = None,
) -> DebtorDetailResponse:
    return await service.get_debtor(debtor_id, session, portfolio_id)


@router.get(
    "/{debtor_id}/related-contacts",
    response_model=RelatedContactsResponse,
    summary="Obtener red de contactos del deudor",
    description="Retorna el deudor titular y sus co-deudores con direcciones y métodos de contacto.",
)
async def get_related_contacts(
    debtor_id: int,
    session: CurrentSession,
    service: DebtorServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> RelatedContactsResponse:
    return await service.get_related_contacts(debtor_id, portfolio_id, session)


@router.get(
    "/{debtor_id}/credits",
    response_model=list[DebtorCreditResponse],
    summary="Créditos del deudor en un portafolio",
    description="Lista de créditos del deudor (como titular) en el portafolio dado.",
)
async def get_debtor_credits(
    debtor_id: int,
    session: CurrentSession,
    service: DebtorServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> list[DebtorCreditResponse]:
    return await service.get_debtor_credits(debtor_id, portfolio_id, session)


@router.post(
    "/",
    response_model=DebtorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear deudor",
)
async def create_debtor(
    data: CreateDebtorRequest,
    session: CurrentSession,
    service: DebtorServiceDep,
) -> DebtorResponse:
    debtor = await service.create_debtor(data)
    return DebtorResponse(
        id=debtor.id,
        full_name=debtor.full_name,
        debtor_type=debtor.debtor_type,
        document_type=debtor.document_type,
        document_number=data.document_number,
    )


@router.post(
    "/{debtor_id}/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar dirección al deudor",
)
async def create_address(
    debtor_id: int,
    data: CreateAddressRequest,
    session: CurrentSession,
    service: DebtorServiceDep,
) -> AddressResponse:
    address = await service.create_address(debtor_id, data)
    return AddressResponse.model_validate(address)


@router.post(
    "/{debtor_id}/contact-methods",
    response_model=ContactMethodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar método de contacto al deudor",
)
async def create_contact_method(
    debtor_id: int,
    data: CreateContactMethodRequest,
    session: CurrentSession,
    service: DebtorServiceDep,
) -> ContactMethodResponse:
    contact = await service.create_contact_method(debtor_id, data)
    return ContactMethodResponse.model_validate(contact)

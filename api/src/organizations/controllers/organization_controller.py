import uuid
from pathlib import Path
from typing import Literal

from fastapi import File, Form, HTTPException, UploadFile, status

from config.api_router import APIRouter
from countries.enums.country_enums import Nationality, UserDocumentType
from onboarding.dependencies import CurrentScope
from organizations.dependencies import AdminScopeDep, OrgServiceDep
from support.dependencies import SupportServiceDep
from organizations.schemas.organization_schemas import (
    OrgRegisterResponse,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    RepresentativeMode,
)
from security.dependencies import CurrentSession
from tools.file_tools import save_org_document_bytes
from users.dependencies import UserServiceDep

router = APIRouter(prefix="/organizations", tags=["Organizaciones"])


@router.get(
    "/",
    response_model=list[OrganizationResponse],
    summary="Listar organizaciones del usuario",
)
async def list_organizations(
    session: CurrentSession,
    scope: CurrentScope,
    service: OrgServiceDep,
) -> list[OrganizationResponse]:
    return await service.get_for_user(session.user_id, scope)


@router.get(
    "/{org_id}",
    response_model=OrganizationResponse,
    summary="Obtener organización por ID",
)
async def get_organization(
    org_id: uuid.UUID,
    _: CurrentSession,
    service: OrgServiceDep,
) -> OrganizationResponse:
    return await service.get_by_id(org_id)


@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear organización",
)
async def create_organization(
    body: OrganizationCreate,
    session: CurrentSession,
    admin_scope: AdminScopeDep,
    service: OrgServiceDep,
    user_service: UserServiceDep,
) -> OrganizationResponse:
    org = await service.create_organization(body, session.user_id, admin_scope)
    await user_service.get_user_session(session.user_id)
    return org


@router.patch(
    "/{org_id}",
    response_model=OrganizationResponse,
    summary="Actualizar datos de la organización",
)
async def update_organization(
    org_id: uuid.UUID,
    body: OrganizationUpdate,
    session: CurrentSession,
    admin_scope: AdminScopeDep,
    service: OrgServiceDep,
) -> OrganizationResponse:
    return await service.update_organization(org_id, body, session.user_id, admin_scope)


@router.patch(
    "/{org_id}/documents/{doc_type}",
    response_model=OrganizationResponse,
    summary="Actualizar documento de la organización",
)
async def update_org_document(
    org_id: uuid.UUID,
    doc_type: Literal["fiscal", "mercantil", "representante"],
    session: CurrentSession,
    admin_scope: AdminScopeDep,
    service: OrgServiceDep,
    file: UploadFile = File(...),
) -> OrganizationResponse:
    org = await service.get_by_id(org_id)
    file_bytes = await file.read()
    ext = Path(file.filename or "").suffix or ".pdf"
    file_path = save_org_document_bytes(file_bytes, str(org_id), doc_type, ext)
    field_map = {
        "fiscal": "fiscal_document_file",
        "mercantil": "mercantile_document_file",
        "representante": "representative_document_file",
    }
    setattr(org, field_map[doc_type], file_path)
    updated = await service.org_repo.update(org)
    return updated


@router.delete(
    "/{org_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar organización",
)
async def delete_organization(
    org_id: uuid.UUID,
    session: CurrentSession,
    admin_scope: AdminScopeDep,
    service: OrgServiceDep,
) -> None:
    await service.delete_organization(org_id, session.user_id, admin_scope)


@router.post(
    "/register",
    response_model=OrgRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar organización con documentos",
    description="Crea una organización con sus documentos fiscales, mercantiles y del representante legal. Genera automáticamente un ticket de verificación.",
)
async def register_organization(
    session: CurrentSession,
    admin_scope: AdminScopeDep,
    service: OrgServiceDep,
    user_service: UserServiceDep,
    support_service: SupportServiceDep,
    name: str = Form(...),
    country: Nationality = Form(...),
    fiscal_document_number: str | None = Form(None),
    description: str | None = Form(None),
    representative_mode: RepresentativeMode = Form(...),
    representative_user_id: int | None = Form(None),
    rep_firstname: str | None = Form(None),
    rep_lastname: str | None = Form(None),
    rep_email: str | None = Form(None),
    rep_document_type: UserDocumentType | None = Form(None),
    rep_document_number: str | None = Form(None),
    fiscal_document_file: UploadFile = File(...),
    mercantile_document_file: UploadFile = File(...),
    representative_document_file: UploadFile = File(...),
) -> OrgRegisterResponse:
    fiscal_bytes = await fiscal_document_file.read()
    fiscal_ext = Path(fiscal_document_file.filename or "").suffix or ".pdf"
    mercantile_bytes = await mercantile_document_file.read()
    mercantile_ext = Path(mercantile_document_file.filename or "").suffix or ".pdf"
    rep_bytes = await representative_document_file.read()
    rep_ext = Path(representative_document_file.filename or "").suffix or ".pdf"
    org = await service.register_with_representative(
        name=name,
        description=description,
        country=country,
        fiscal_document_number=fiscal_document_number,
        representative_mode=representative_mode,
        representative_user_id=representative_user_id,
        rep_firstname=rep_firstname,
        rep_lastname=rep_lastname,
        rep_email=rep_email,
        rep_document_type=rep_document_type,
        rep_document_number=rep_document_number,
        fiscal_file_bytes=fiscal_bytes,
        fiscal_file_ext=fiscal_ext,
        mercantile_file_bytes=mercantile_bytes,
        mercantile_file_ext=mercantile_ext,
        representative_file_bytes=rep_bytes,
        representative_file_ext=rep_ext,
        created_by_user_id=session.user_id,
        scope=admin_scope,
    )
    await support_service.create_org_verification_ticket(org.id, session.user_id)
    await user_service.get_user_session(session.user_id)
    return org

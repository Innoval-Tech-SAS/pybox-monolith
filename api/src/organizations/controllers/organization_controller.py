import uuid
from pathlib import Path

from fastapi import File, Form, UploadFile, status

from config.api_router import APIRouter
from countries.enums.country_enums import Nationality, UserDocumentType
from onboarding.dependencies import CurrentUser, CurrentScope
from organizations.dependencies import AdminAssignmentDep, OrgServiceDep
from organizations.schemas.organization_schemas import (
    OrgRegisterResponse,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    RepresentativeMode,
)
from users.enums.user_enums import UserScope

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=list[OrganizationResponse])
async def list_organizations(
    user: CurrentUser,
    scope: CurrentScope,
    service: OrgServiceDep,
) -> list[OrganizationResponse]:
    return await service.get_for_user(user.id, scope)


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: uuid.UUID,
    _: CurrentUser,
    service: OrgServiceDep,
) -> OrganizationResponse:
    return await service.get_by_id(org_id)


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    body: OrganizationCreate,
    user: CurrentUser,
    admin: AdminAssignmentDep,
    service: OrgServiceDep,
) -> OrganizationResponse:
    return await service.create_organization(body, user.id, admin.scope)


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: uuid.UUID,
    body: OrganizationUpdate,
    user: CurrentUser,
    admin: AdminAssignmentDep,
    service: OrgServiceDep,
) -> OrganizationResponse:
    return await service.update_organization(org_id, body, user.id, admin.scope)


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: uuid.UUID,
    user: CurrentUser,
    admin: AdminAssignmentDep,
    service: OrgServiceDep,
) -> None:
    await service.delete_organization(org_id, user.id, admin.scope)


@router.post("/register", response_model=OrgRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_organization(
    user: CurrentUser,
    admin: AdminAssignmentDep,
    service: OrgServiceDep,
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
    mercantile_document_file: UploadFile = File(...),
    representative_document_file: UploadFile = File(...),
) -> OrgRegisterResponse:
    mercantile_bytes = await mercantile_document_file.read()
    mercantile_ext = Path(mercantile_document_file.filename or "").suffix or ".pdf"

    rep_bytes = await representative_document_file.read()
    rep_ext = Path(representative_document_file.filename or "").suffix or ".pdf"

    return await service.register_with_representative(
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
        mercantile_file_bytes=mercantile_bytes,
        mercantile_file_ext=mercantile_ext,
        representative_file_bytes=rep_bytes,
        representative_file_ext=rep_ext,
        created_by_user_id=user.id,
        scope=admin.scope,
    )

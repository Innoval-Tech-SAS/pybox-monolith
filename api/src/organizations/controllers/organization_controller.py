import uuid

from fastapi import status

from config.api_router import APIRouter
from onboarding.dependencies import CurrentUser
from organizations.dependencies import AdminAssignmentDep, OrgServiceDep
from organizations.schemas.organization_schemas import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from users.enums.user_enums import UserScope

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=list[OrganizationResponse])
async def list_organizations(
    _: CurrentUser,
    service: OrgServiceDep,
) -> list[OrganizationResponse]:
    return await service.get_all()


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

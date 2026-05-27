import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_main_session
from security.dependencies import CurrentSession
from support.schemas.support_schemas import SupportFilter
from support.services.support_service import SupportService
from users.enums.user_enums import UserRole, UserScope


_STAFF_ROLES = {UserRole.ADMIN, UserRole.CUSTOMER_SERVICE}


def get_support_filter(
    session: CurrentSession,
    include_resolved: bool = Query(False, alias="includeResolved"),
) -> SupportFilter:
    is_admin = session.role == UserRole.ADMIN

    if session.role in _STAFF_ROLES:
        if session.scope == UserScope.GLOBAL:
            return SupportFilter(
                include_resolved=include_resolved,
                can_resolve=True,
                can_assign=is_admin,
            )
        if session.scope == UserScope.ORGANIZATION:
            org_ids = [uuid.UUID(o) for o in session.orgs]
            return SupportFilter(
                org_ids=org_ids,
                include_resolved=include_resolved,
                can_resolve=True,
                can_assign=is_admin,
            )

    if session.role in {UserRole.USER_ORGANIZATION, UserRole.USER}:
        return SupportFilter(created_by=session.user_id, include_resolved=True)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")


def get_support_service(
    db: Annotated[AsyncSession, Depends(get_main_session)],
) -> SupportService:
    return SupportService(db)


SupportServiceDep = Annotated[SupportService, Depends(get_support_service)]
SupportAccessFilter = Annotated[SupportFilter, Depends(get_support_filter)]

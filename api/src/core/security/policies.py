import uuid
from typing import Awaitable, Callable

from fastapi import HTTPException, status

from identity.users.enums.user_enums import UserRole
from identity.users.schemas.user_session_schema import UserSession

# Tupla (document_type, document_number) usada para filtrar queries de deudores
SelfIdentity = tuple[str, str]


def require_global(session: UserSession) -> None:
    if not session.is_global:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo usuarios globales pueden realizar esta acción")


def require_global_admin(session: UserSession) -> None:
    if not session.is_global or session.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acceso restringido a administradores globales")


def require_org_or_global(session: UserSession) -> None:
    if not session.is_global and not session.orgs:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso")


def require_org_admin(session: UserSession, org_id: str) -> None:
    if session.is_global:
        return
    org_entry = session.orgs.get(org_id)
    if org_entry is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso a esta organización")
    if org_entry.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo administradores pueden realizar esta acción")


def require_permission(perm: str, session: UserSession, org_id: str) -> None:
    if session.is_global:
        return
    ctx = session.orgs.get(org_id)
    if not ctx:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso a esta organización")
    if perm not in ctx.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permisos para esta acción")


def require_org_access(session: UserSession, org_id: str) -> None:
    if session.is_global:
        return
    if org_id not in session.orgs:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso a esta organización")


def get_self_identity(session: UserSession) -> SelfIdentity:
    if not session.document_type or not session.document_number:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Completa tu documento de identidad para continuar",
        )
    return session.document_type, session.document_number


async def require_portfolio_access(
    session: UserSession,
    org_id: str,
    portfolio_id: uuid.UUID,
    check_access: Callable[[uuid.UUID, uuid.UUID, str], Awaitable[bool]],
) -> None:
    if session.is_global:
        return
    org_entry = session.orgs.get(org_id)
    if org_entry is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso a esta organización")
    if org_entry.role == UserRole.ADMIN:
        return
    allowed = await check_access(session.user_id, portfolio_id, org_id)
    if not allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso a este portafolio")

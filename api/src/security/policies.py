from typing import Awaitable, Callable

from fastapi import HTTPException, status

from users.schemas.user_session_schema import UserSession

# Tupla (document_type, document_number) usada para filtrar queries de deudores
SelfIdentity = tuple[str, str]


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
    portfolio_id: int,
    check_access: Callable[[int, int, str], Awaitable[bool]],
) -> None:
    if session.is_global:
        return
    if org_id not in session.orgs:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso a esta organización")
    allowed = await check_access(session.user_id, portfolio_id, org_id)
    if not allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso a este portafolio")

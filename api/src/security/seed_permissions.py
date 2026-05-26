from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models.permission_model import PermissionModel
from security.permissions import (
    ORG_PORTFOLIOS, ORG_PAYMENT_METHODS, ORG_REPORTS,
    PORTFOLIO_CLIENTS, PORTFOLIO_UPLOAD_NEW, PORTFOLIO_UPLOAD_UPDATE,
)

_PERMISSIONS: list[tuple[str, str]] = [
    (ORG_PORTFOLIOS,          "Módulo: Mis Portafolios"),
    (ORG_PAYMENT_METHODS,     "Módulo: Métodos de Pago"),
    (ORG_REPORTS,             "Módulo: Reportes"),
    (PORTFOLIO_CLIENTS,       "Módulo: Clientes"),
    (PORTFOLIO_UPLOAD_NEW,    "Módulo: Subir nuevos clientes"),
    (PORTFOLIO_UPLOAD_UPDATE, "Módulo: Actualizar clientes"),
]


async def seed_permissions(session: AsyncSession) -> None:
    existing = set(
        row[0]
        for row in (await session.execute(select(PermissionModel.name))).all()
    )
    new_permissions = [
        PermissionModel(name=name, label=label)
        for name, label in _PERMISSIONS
        if name not in existing
    ]
    if new_permissions:
        session.add_all(new_permissions)
        await session.commit()

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from users.models.permission_model import PermissionModel
from security.permissions import (
    ORG_PORTFOLIOS,
    ORG_PAYMENT_METHODS,
    ORG_REPORTS,
    ORG_USERS,
    ORG_CAMPAIGNS,
    PORTFOLIO_CLIENTS,
    PORTFOLIO_CALENDAR,
    PORTFOLIO_COMMUNICATIONS,
    PORTFOLIO_UPLOAD_NEW,
    PORTFOLIO_UPLOAD_UPDATE,
)

_PERMISSIONS: list[tuple[str, str]] = [
    (ORG_PORTFOLIOS, "Mis Portafolios"),
    (ORG_PAYMENT_METHODS, "Métodos de Pago"),
    (ORG_REPORTS, "Reportes"),
    (ORG_USERS, "Usuarios"),
    (ORG_CAMPAIGNS, "Campañas"),
    (PORTFOLIO_CLIENTS, "Clientes"),
    (PORTFOLIO_UPLOAD_NEW, "Subir nuevos clientes"),
    (PORTFOLIO_UPLOAD_UPDATE, "Actualizar clientes"),
    (PORTFOLIO_COMMUNICATIONS, "Comunicaciones"),
    (PORTFOLIO_CALENDAR, "Calendario"),
]


async def seed_permissions(session: AsyncSession) -> None:
    existing = {
        row[0] for row in (await session.execute(select(PermissionModel.name))).all()
    }
    new_permissions = []
    for name, label in _PERMISSIONS:
        if name not in existing:
            new_permissions.append(PermissionModel(name=name, label=label))
        else:
            await session.execute(
                update(PermissionModel)
                .where(PermissionModel.name == name)
                .values(label=label)
            )
    if new_permissions:
        session.add_all(new_permissions)
    await session.commit()

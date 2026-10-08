"""Dependencia de FastAPI para inyectar el PaymentMethodService."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database import get_main_session
from receivables.payment_methods.repository.payment_method_repository import (
    PaymentMethodRepository,
)
from receivables.payment_methods.services.payment_method_service import (
    PaymentMethodService,
)


def get_payment_method_service(
    session: Annotated[AsyncSession, Depends(get_main_session)],
) -> PaymentMethodService:
    return PaymentMethodService(session, PaymentMethodRepository(session))


PaymentMethodServiceDep = Annotated[
    PaymentMethodService, Depends(get_payment_method_service)
]

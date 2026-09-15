"""Tests de `PaymentMethodService`: no existía ningún test para este dominio --
ni de servicio ni de controller -- pese a que persiste datos sensibles (número de
cuenta cifrado). Cubre CRUD completo, el filtro is_active, el 404 cross-organización,
el update parcial (solo pisa los campos que vienen en el request) y el round-trip de
cifrado del número de cuenta.
"""

import uuid

import pytest
from fastapi import HTTPException

from receivables.payment_methods.enums.payment_method_enums import PaymentMethodType
from receivables.payment_methods.repository.payment_method_repository import PaymentMethodRepository
from receivables.payment_methods.schemas.payment_method_schemas import (
    PaymentMethodCreateRequest,
    PaymentMethodUpdateRequest,
)
from receivables.payment_methods.services.payment_method_service import PaymentMethodService
from tests.receivables.conftest import build_organization


async def _service(db_session) -> PaymentMethodService:
    return PaymentMethodService(db_session, PaymentMethodRepository(db_session))


async def _org(db_session):
    org = build_organization()
    db_session.add(org)
    await db_session.flush()
    return org


class TestCreate:
    async def test_creates_and_encrypts_account_number(self, db_session):
        org = await _org(db_session)
        service = await _service(db_session)
        data = PaymentMethodCreateRequest(
            organization_id=org.id, name="  Cuenta Bancolombia  ", type=PaymentMethodType.BANK_TRANSFER,
            account_number="1234567890",
        )

        result = await service.create(data)

        assert result.name == "Cuenta Bancolombia"
        assert result.account_number == "1234567890"
        assert result.is_active is True

        row = await PaymentMethodRepository(db_session).get_by_id(result.id)
        assert row.account_number != "1234567890"  # persiste cifrado, no en claro

    async def test_creates_without_account_number(self, db_session):
        org = await _org(db_session)
        service = await _service(db_session)
        data = PaymentMethodCreateRequest(organization_id=org.id, name="Efectivo", type=PaymentMethodType.CASH)

        result = await service.create(data)

        assert result.account_number is None


class TestList:
    async def test_lists_only_active_when_filtered(self, db_session):
        org = await _org(db_session)
        service = await _service(db_session)
        active = await service.create(
            PaymentMethodCreateRequest(organization_id=org.id, name="Activo", type=PaymentMethodType.CASH)
        )
        inactive = await service.create(
            PaymentMethodCreateRequest(organization_id=org.id, name="Inactivo", type=PaymentMethodType.CASH)
        )
        await service.update(inactive.id, org.id, PaymentMethodUpdateRequest(is_active=False))

        only_active = await service.list(org.id, is_active=True)
        everything = await service.list(org.id, is_active=None)

        assert {m.id for m in only_active} == {active.id}
        assert {m.id for m in everything} == {active.id, inactive.id}

    async def test_scoped_to_organization(self, db_session):
        org_a = await _org(db_session)
        org_b = await _org(db_session)
        service = await _service(db_session)
        await service.create(PaymentMethodCreateRequest(organization_id=org_a.id, name="A", type=PaymentMethodType.CASH))
        await service.create(PaymentMethodCreateRequest(organization_id=org_b.id, name="B", type=PaymentMethodType.CASH))

        result = await service.list(org_a.id)

        assert len(result) == 1
        assert result[0].name == "A"


class TestGet:
    async def test_not_found_raises_404(self, db_session):
        org = await _org(db_session)
        service = await _service(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await service.get(uuid.uuid4(), org.id)
        assert exc_info.value.status_code == 404

    async def test_wrong_organization_raises_404(self, db_session):
        org_a = await _org(db_session)
        org_b = await _org(db_session)
        service = await _service(db_session)
        method = await service.create(
            PaymentMethodCreateRequest(organization_id=org_a.id, name="A", type=PaymentMethodType.CASH)
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.get(method.id, org_b.id)
        assert exc_info.value.status_code == 404


class TestUpdate:
    async def test_partial_update_only_overwrites_fields_that_were_set(self, db_session):
        org = await _org(db_session)
        service = await _service(db_session)
        method = await service.create(
            PaymentMethodCreateRequest(
                organization_id=org.id, name="Original", type=PaymentMethodType.BANK_TRANSFER,
                bank_name="Banco X", account_number="111",
            )
        )

        result = await service.update(method.id, org.id, PaymentMethodUpdateRequest(bank_name="Banco Y"))

        assert result.bank_name == "Banco Y"
        assert result.name == "Original"
        assert result.account_number == "111"

    async def test_updates_account_number_re_encrypts(self, db_session):
        org = await _org(db_session)
        service = await _service(db_session)
        method = await service.create(
            PaymentMethodCreateRequest(
                organization_id=org.id, name="X", type=PaymentMethodType.BANK_TRANSFER, account_number="111",
            )
        )

        result = await service.update(method.id, org.id, PaymentMethodUpdateRequest(account_number="222"))

        assert result.account_number == "222"

    async def test_not_found_raises_404(self, db_session):
        org = await _org(db_session)
        service = await _service(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await service.update(uuid.uuid4(), org.id, PaymentMethodUpdateRequest(name="X"))
        assert exc_info.value.status_code == 404


class TestDelete:
    async def test_soft_deletes_and_excludes_from_list(self, db_session):
        org = await _org(db_session)
        service = await _service(db_session)
        method = await service.create(
            PaymentMethodCreateRequest(organization_id=org.id, name="A", type=PaymentMethodType.CASH)
        )

        await service.delete(method.id, org.id)

        row = await PaymentMethodRepository(db_session).get_by_id_including_deleted(method.id)
        assert row is not None and row.deleted_at is not None
        assert await service.list(org.id) == []

    async def test_not_found_raises_404(self, db_session):
        org = await _org(db_session)
        service = await _service(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await service.delete(uuid.uuid4(), org.id)
        assert exc_info.value.status_code == 404

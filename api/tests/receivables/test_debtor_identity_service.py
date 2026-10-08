"""Validación de identidad del titular que escribe por WhatsApp (flujo de n8n).

La búsqueda cruza organizaciones a propósito (el mensaje no trae empresa y el mismo documento
puede ser deudores distintos en varias), así que lo que se fija aquí es que ese cruce no filtre
nada más que una pista enmascarada, que respete los borrados lógicos y que el dato de
confirmación no se pueda adivinar por fuerza bruta.
"""

from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from core.database.redis import redis_client
from core.security.services.encrypt_service import encrypt_service
from receivables.contact_methods.enums.contact_method_enums import ContactMethodType
from receivables.contact_methods.models.contact_method_model import ContactMethodModel
from receivables.contact_methods.repository.contact_method_repository import ContactMethodRepository
from receivables.debtors.constants.debtor_identity_constants import IDENTITY_VERIFY_MAX_ATTEMPTS
from receivables.debtors.enums.debtor_enums import DebtorType
from receivables.debtors.enums.debtor_identity_enums import IdentityChannel
from receivables.debtors.repository.debtor_repository import DebtorRepository
from receivables.debtors.schemas.debtor_identity_schemas import IdentityChallengeRequest, IdentityVerifyRequest
from receivables.debtors.services.debtor_identity_service import DebtorIdentityService
from tests.factories import unique_document_number
from tests.receivables.conftest import add_organization, build_debtor


def build_service(db_session) -> DebtorIdentityService:
    return DebtorIdentityService(
        debtor_repo=DebtorRepository(db_session),
        contact_repo=ContactMethodRepository(db_session),
    )


async def add_debtor(db_session, org_id, doc_number, *, emails=(), phones=(), debtor_type=DebtorType.DEBTOR):
    debtor = build_debtor(org_id, document_number_plain=doc_number, debtor_type=debtor_type)
    db_session.add(debtor)
    await db_session.flush()
    for email in emails:
        db_session.add(ContactMethodModel(contact_type=ContactMethodType.EMAIL, contact_value=email, debtor_id=debtor.id))
    for phone in phones:
        db_session.add(ContactMethodModel(contact_type=ContactMethodType.PHONE, contact_value=phone, debtor_id=debtor.id))
    await db_session.flush()
    return debtor


def challenge(doc_number, doc_type="CC") -> IdentityChallengeRequest:
    return IdentityChallengeRequest(document_type=doc_type, document_number=doc_number)


def verify(doc_number, channel, value, doc_type="CC") -> IdentityVerifyRequest:
    return IdentityVerifyRequest(document_type=doc_type, document_number=doc_number, channel=channel, value=value)


class TestRequestChallenge:
    async def test_unknown_document_is_not_available(self, db_session):
        result = await build_service(db_session).request_challenge(challenge(unique_document_number()))

        assert result.available is False
        assert result.channel is None and result.hint is None

    async def test_debtor_with_email_gets_the_masked_email_hint(self, db_session):
        org = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org.id, doc, emails=["dev.innovaltect@gmail.com"])

        result = await build_service(db_session).request_challenge(challenge(doc))

        assert result.available is True
        assert result.channel == IdentityChannel.EMAIL
        assert result.hint == "de*************@*****.com"

    async def test_falls_back_to_phone_when_no_debtor_row_has_an_email(self, db_session):
        org = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org.id, doc, phones=["573001234567"])

        result = await build_service(db_session).request_challenge(challenge(doc))

        assert result.channel == IdentityChannel.PHONE
        assert result.hint == "********4567"

    async def test_debtor_without_any_contact_is_not_available(self, db_session):
        org = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org.id, doc)

        assert (await build_service(db_session).request_challenge(challenge(doc))).available is False

    async def test_document_type_must_match(self, db_session):
        org = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org.id, doc, emails=["a@b.co"])

        result = await build_service(db_session).request_challenge(challenge(doc, doc_type="CE"))

        assert result.available is False

    async def test_email_from_another_organization_row_counts(self, db_session):
        """El mismo documento en dos empresas: el correo puede estar en cualquiera."""
        org_a = await add_organization(db_session)
        org_b = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org_a.id, doc)
        await add_debtor(db_session, org_b.id, doc, emails=["persona@correo.com"])

        result = await build_service(db_session).request_challenge(challenge(doc))

        assert result.channel == IdentityChannel.EMAIL

    async def test_soft_deleted_debtor_is_ignored(self, db_session):
        org = await add_organization(db_session)
        doc = unique_document_number()
        debtor = await add_debtor(db_session, org.id, doc, emails=["persona@correo.com"])
        debtor.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        assert (await build_service(db_session).request_challenge(challenge(doc))).available is False

    async def test_soft_deleted_contact_method_is_ignored(self, db_session):
        org = await add_organization(db_session)
        doc = unique_document_number()
        debtor = await add_debtor(db_session, org.id, doc, emails=["borrado@correo.com"])
        contacts = await ContactMethodRepository(db_session).get_by_debtor_id(debtor.id)
        contacts[0].deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        assert (await build_service(db_session).request_challenge(challenge(doc))).available is False


class TestOnlyHoldersAreValidated:
    """La validación aplica a titulares; un co-deudor no se identifica por este canal."""

    async def test_co_debtor_alone_is_not_available(self, db_session):
        org = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org.id, doc, emails=["codeudor@correo.com"], debtor_type=DebtorType.CO_DEBTOR)

        assert (await build_service(db_session).request_challenge(challenge(doc))).available is False

    async def test_co_debtor_alone_never_verifies(self, db_session):
        org = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org.id, doc, emails=["codeudor@correo.com"], debtor_type=DebtorType.CO_DEBTOR)

        result = await build_service(db_session).verify(verify(doc, IdentityChannel.EMAIL, "codeudor@correo.com"))

        assert result.verified is False

    async def test_contacts_of_the_co_debtor_row_do_not_validate_the_holder(self, db_session):
        """Titular en una empresa (sin contactos) y co-deudor en otra (con correo): el
        correo de la fila de co-deudor no cuenta."""
        org_a = await add_organization(db_session)
        org_b = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org_a.id, doc)
        await add_debtor(db_session, org_b.id, doc, emails=["codeudor@correo.com"], debtor_type=DebtorType.CO_DEBTOR)
        service = build_service(db_session)

        assert (await service.request_challenge(challenge(doc))).available is False
        assert (await service.verify(verify(doc, IdentityChannel.EMAIL, "codeudor@correo.com"))).verified is False

    async def test_holder_row_still_works_when_the_same_person_is_co_debtor_elsewhere(self, db_session):
        org_a = await add_organization(db_session)
        org_b = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org_a.id, doc, emails=["titular@correo.com"])
        await add_debtor(db_session, org_b.id, doc, emails=["codeudor@correo.com"], debtor_type=DebtorType.CO_DEBTOR)
        service = build_service(db_session)

        assert (await service.request_challenge(challenge(doc))).hint == "ti*****@******.com"
        assert (await service.verify(verify(doc, IdentityChannel.EMAIL, "titular@correo.com"))).verified is True


class TestVerify:
    async def test_email_match_ignores_case_and_spaces(self, db_session):
        org = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org.id, doc, emails=["Persona@Correo.com"])

        result = await build_service(db_session).verify(verify(doc, IdentityChannel.EMAIL, "  persona@correo.COM "))

        assert result.verified is True

    async def test_wrong_email_is_rejected(self, db_session):
        org = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org.id, doc, emails=["persona@correo.com"])

        assert (await build_service(db_session).verify(verify(doc, IdentityChannel.EMAIL, "otra@correo.com"))).verified is False

    async def test_any_registered_email_across_organizations_verifies(self, db_session):
        org_a = await add_organization(db_session)
        org_b = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org_a.id, doc, emails=["uno@correo.com"])
        await add_debtor(db_session, org_b.id, doc, emails=["dos@correo.com"])

        service = build_service(db_session)

        assert (await service.verify(verify(doc, IdentityChannel.EMAIL, "dos@correo.com"))).verified is True

    async def test_unknown_document_never_verifies(self, db_session):
        result = await build_service(db_session).verify(
            verify(unique_document_number(), IdentityChannel.EMAIL, "persona@correo.com")
        )

        assert result.verified is False

    async def test_a_registered_email_of_another_person_does_not_verify(self, db_session):
        """El correo correcto de OTRO titular no valida este documento."""
        org = await add_organization(db_session)
        doc_a, doc_b = unique_document_number(), unique_document_number()
        await add_debtor(db_session, org.id, doc_a, emails=["a@correo.com"])
        await add_debtor(db_session, org.id, doc_b, emails=["b@correo.com"])

        assert (await build_service(db_session).verify(verify(doc_a, IdentityChannel.EMAIL, "b@correo.com"))).verified is False

    @pytest.mark.parametrize("typed", ["3001234567", "573001234567", "+57 300 123 4567"])
    async def test_phone_matches_with_or_without_country_code(self, db_session, typed):
        org = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org.id, doc, phones=["573001234567"])

        assert (await build_service(db_session).verify(verify(doc, IdentityChannel.PHONE, typed))).verified is True

    async def test_too_short_phone_never_verifies(self, db_session):
        org = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org.id, doc, phones=["573001234567"])

        assert (await build_service(db_session).verify(verify(doc, IdentityChannel.PHONE, "4567"))).verified is False

    async def test_attempts_are_capped_per_document(self, db_session):
        org = await add_organization(db_session)
        doc = unique_document_number()
        await add_debtor(db_session, org.id, doc, emails=["persona@correo.com"])
        service = build_service(db_session)

        for _ in range(IDENTITY_VERIFY_MAX_ATTEMPTS):
            assert (await service.verify(verify(doc, IdentityChannel.EMAIL, "mal@correo.com"))).verified is False

        with pytest.raises(HTTPException) as exc:
            await service.verify(verify(doc, IdentityChannel.EMAIL, "persona@correo.com"))
        assert exc.value.status_code == 429

    async def test_attempt_counters_do_not_share_between_documents(self, db_session):
        org = await add_organization(db_session)
        doc_a, doc_b = unique_document_number(), unique_document_number()
        await add_debtor(db_session, org.id, doc_b, emails=["persona@correo.com"])
        service = build_service(db_session)

        for _ in range(IDENTITY_VERIFY_MAX_ATTEMPTS):
            await service.verify(verify(doc_a, IdentityChannel.EMAIL, "x@correo.com"))

        assert (await service.verify(verify(doc_b, IdentityChannel.EMAIL, "persona@correo.com"))).verified is True

    async def test_attempt_key_does_not_contain_the_plain_document(self, db_session, fake_redis):
        doc = unique_document_number()
        await build_service(db_session).verify(verify(doc, IdentityChannel.EMAIL, "x@correo.com"))

        stored_keys = list(getattr(fake_redis, "_store", {}) or getattr(fake_redis, "store", {}))
        assert stored_keys, "el contador de intentos debería existir en Redis"
        assert all(doc not in key for key in stored_keys)
        assert any(encrypt_service.hash_document(doc) in key for key in stored_keys)

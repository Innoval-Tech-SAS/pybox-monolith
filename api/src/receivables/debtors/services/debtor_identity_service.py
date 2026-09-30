"""Verificación de identidad del deudor por challenge/confirmación (email/teléfono)."""

import hmac

from fastapi import HTTPException, status

from core.database.redis import redis_client
from core.security.services.encrypt_service import encrypt_service
from receivables.contact_methods.enums.contact_method_enums import ContactMethodType
from receivables.contact_methods.repository.contact_method_repository import (
    ContactMethodRepository,
)
from receivables.contact_methods.utils.contact_normalize import normalize_email
from receivables.debtors.constants.debtor_identity_constants import (
    IDENTITY_VERIFY_KEY_PREFIX,
    IDENTITY_VERIFY_MAX_ATTEMPTS,
    IDENTITY_VERIFY_WINDOW_SECONDS,
)
from receivables.debtors.enums.debtor_identity_enums import IdentityChannel
from receivables.debtors.models.debtor_model import DebtorModel
from receivables.debtors.repository.debtor_repository import DebtorRepository
from receivables.debtors.schemas.debtor_identity_schemas import (
    IdentityChallengeRequest,
    IdentityChallengeResponse,
    IdentityVerifyRequest,
    IdentityVerifyResponse,
)
from receivables.debtors.utils.identity_mask_utils import (
    mask_email,
    mask_phone,
    phone_compare_key,
)


class DebtorIdentityService:
    """Valida la identidad de un titular que escribe por WhatsApp (flujo
    conversacional de n8n).

    EXCEPCIÓN DELIBERADA AL ALCANCE POR ORGANIZACIÓN: quien escribe no llega con
    una organización, y el mismo documento puede figurar como deudores
    independientes en varias empresas. La identidad es de la persona, no de una
    empresa, así que la búsqueda cruza organizaciones (mismo criterio que el
    autoservicio SELF, ``list_by_document``).

    No hay sesión de usuario: la autorización la da la llave de servicio del gate
    de la ruta (``require_n8n_service_key``). Para no convertir el cruce en una
    fuga, jamás se devuelven ids, nombres, organizaciones ni el dato completo:
    solo una pista enmascarada y un booleano.

    Solo aplica a titulares (``DebtorType.DEBTOR``); los co-deudores quedan fuera.
    """

    def __init__(
        self, debtor_repo: DebtorRepository, contact_repo: ContactMethodRepository
    ):
        self._debtor_repo = debtor_repo
        self._contact_repo = contact_repo

    async def request_challenge(
        self, data: IdentityChallengeRequest
    ) -> IdentityChallengeResponse:
        """Elige el dato con el que el titular debe confirmarse: primero el correo y, si
        ninguna de sus filas de deudor tiene uno, el teléfono."""
        debtors = await self._find_debtors(data.document_type, data.document_number)

        emails = await self._email_values(debtors)
        if emails:
            # Orden estable: la pista no debe cambiar entre llamadas. Cualquier
            # correo registrado valida en `verify`, no solo el que se muestra.
            return IdentityChallengeResponse(
                available=True,
                channel=IdentityChannel.EMAIL,
                hint=mask_email(emails[0]),
            )

        phones = await self._phone_values(debtors)
        if phones:
            return IdentityChallengeResponse(
                available=True,
                channel=IdentityChannel.PHONE,
                hint=mask_phone(phones[0]),
            )

        return IdentityChallengeResponse(available=False)

    async def verify(self, data: IdentityVerifyRequest) -> IdentityVerifyResponse:
        await self._enforce_attempt_limit(data.document_type, data.document_number)
        debtors = await self._find_debtors(data.document_type, data.document_number)

        if data.channel == IdentityChannel.EMAIL:
            given = normalize_email(data.value).encode("utf-8")
            candidates = [e.encode("utf-8") for e in await self._email_values(debtors)]
        else:
            key = phone_compare_key(data.value)
            given = (key or "").encode("utf-8")
            candidates = [k.encode("utf-8") for k in await self._phone_keys(debtors)]

        if not given:
            return IdentityVerifyResponse(verified=False)

        # Se recorren todos los candidatos sin cortar en el primero: el tiempo de
        # respuesta no debe revelar cuál de los datos registrados coincidió.
        verified = False
        for candidate in candidates:
            if hmac.compare_digest(candidate, given):
                verified = True
        return IdentityVerifyResponse(verified=verified)

    async def _find_debtors(
        self, document_type, document_number: str
    ) -> list[DebtorModel]:
        doc_hash = encrypt_service.hash_document(document_number)
        # Solo titulares: un co-deudor no se valida por este canal, ni sus
        # contactos sirven para validar al titular de otra fila con el mismo
        # documento.
        return await self._debtor_repo.list_holders_by_document(document_type, doc_hash)

    async def _email_values(self, debtors: list[DebtorModel]) -> list[str]:
        raw = await self._contact_values(debtors, ContactMethodType.EMAIL)
        return sorted({normalize_email(v) for v in raw if normalize_email(v)})

    async def _phone_values(self, debtors: list[DebtorModel]) -> list[str]:
        raw = await self._contact_values(debtors, ContactMethodType.PHONE)
        return sorted({v for v in raw if phone_compare_key(v)})

    async def _phone_keys(self, debtors: list[DebtorModel]) -> list[str]:
        keys = {phone_compare_key(v) for v in await self._phone_values(debtors)}
        return sorted(k for k in keys if k)

    async def _contact_values(
        self, debtors: list[DebtorModel], contact_type: ContactMethodType
    ) -> list[str]:
        if not debtors:
            return []
        by_debtor = await self._contact_repo.get_all_values_by_debtors(
            [d.id for d in debtors], contact_type
        )
        return [value for values in by_debtor.values() for value in values]

    async def _enforce_attempt_limit(self, document_type, document_number: str) -> None:
        # La llave usa el hash (no el número en claro) para no dejar documentos en
        # Redis.
        doc_hash = encrypt_service.hash_document(document_number)
        key = f"{IDENTITY_VERIFY_KEY_PREFIX}:{document_type}:{doc_hash}"
        attempts = await redis_client.increment(key, IDENTITY_VERIFY_WINDOW_SECONDS)
        if attempts > IDENTITY_VERIFY_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    "Demasiados intentos de verificación. Intenta de nuevo más tarde."
                ),
            )

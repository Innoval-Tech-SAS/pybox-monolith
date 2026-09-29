from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from core.security.services.encrypt_service import encrypt_service
from messaging.provider_credentials.enums.provider_credential_enums import (
    MessagingCredentialProvider,
)
from messaging.provider_credentials.models.provider_credential_model import (
    MessagingProviderCredentialModel,
)
from messaging.provider_credentials.repository.provider_credential_repository import (
    MessagingProviderCredentialRepository,
)


@dataclass(frozen=True)
class DecryptedMessagingCredential:
    """Credencial lista para usar: `values` unifica `public_config` (en claro) con los
    `secrets` YA descifrados. Solo se materializa al momento del envío."""

    country_code: str | None
    provider: MessagingCredentialProvider
    values: dict[str, str]
    lookup_key: str | None

    def get(self, key: str, default: str | None = None) -> str | None:
        return self.values.get(key, default)


class MessagingProviderCredentialService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = MessagingProviderCredentialRepository(session)

    async def get_decrypted(
        self, country_code: str | None, provider: MessagingCredentialProvider
    ) -> DecryptedMessagingCredential | None:
        """Resuelve la credencial del país (o global) y descifra sus secretos. `None`
        si no hay credencial configurada/activa para ese proveedor."""
        return self._to_decrypted(await self._repo.resolve(country_code, provider))

    async def resolve_by_lookup_key(
        self, provider: MessagingCredentialProvider, lookup_key: str
    ) -> DecryptedMessagingCredential | None:
        return self._to_decrypted(
            await self._repo.get_by_lookup_key(provider, lookup_key)
        )

    @staticmethod
    def _to_decrypted(
        row: MessagingProviderCredentialModel | None,
    ) -> DecryptedMessagingCredential | None:
        if row is None or not row.is_active:
            return None
        decrypted = {
            key: encrypt_service.decrypt_to_str(token)
            for key, token in (row.secrets or {}).items()
        }
        values = {**(row.public_config or {}), **decrypted}
        return DecryptedMessagingCredential(
            row.country_code, row.provider, values, row.lookup_key
        )

from __future__ import annotations

from dataclasses import dataclass

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from identity.auth.enums.auth_enums import AuthProvider
from core.config.logger import logger
from core.tools.config_tools import get_or_throw


@dataclass(frozen=True)
class ProviderProfile:
    provider: AuthProvider
    provider_user_id: str
    email: str
    email_verified: bool
    firstname: str | None = None
    lastname: str | None = None


class OAuthProviderService:
    GOOGLE_CLIENT_ID = "GOOGLE_CLIENT_ID"

    def verify_provider_token(
        self,
        provider: AuthProvider,
        token: str,
    ) -> ProviderProfile:
        if provider == AuthProvider.GOOGLE:
            return self._verify_google_token(token)

        raise ValueError("Proveedor de autenticación no soportado.")

    def _verify_google_token(self, token: str) -> ProviderProfile:
        client_id = get_or_throw(self.GOOGLE_CLIENT_ID)
        try:
            payload = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                client_id,
                clock_skew_in_seconds=10,
            )
        except ValueError as error:
            logger.error("[oauth] google_token_error | %s", error)
            raise ValueError("Token de Google inválido.") from error

        email = str(payload.get("email") or "").strip().lower()
        provider_user_id = str(payload.get("sub") or "").strip()
        email_verified = bool(payload.get("email_verified"))

        if not email or not provider_user_id or not email_verified:
            raise ValueError("La cuenta de Google no tiene email verificado.")

        return ProviderProfile(
            provider=AuthProvider.GOOGLE,
            provider_user_id=provider_user_id,
            email=email,
            email_verified=email_verified,
            firstname=payload.get("given_name"),
            lastname=payload.get("family_name"),
        )

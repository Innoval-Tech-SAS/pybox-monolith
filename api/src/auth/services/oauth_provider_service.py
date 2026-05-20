from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from auth.enums.auth_enums import AuthProvider
from tools.config_tools import get_or_throw


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
    FACEBOOK_APP_ID = "FACEBOOK_APP_ID"
    FACEBOOK_APP_SECRET = "FACEBOOK_APP_SECRET"
    FACEBOOK_GRAPH_URL = "https://graph.facebook.com"

    def verify_provider_token(
        self,
        provider: AuthProvider,
        token: str,
    ) -> ProviderProfile:
        if provider == AuthProvider.GOOGLE:
            return self._verify_google_token(token)

        if provider == AuthProvider.FACEBOOK:
            return self._verify_facebook_token(token)

        raise ValueError("Proveedor de autenticación no soportado.")

    def _verify_google_token(self, token: str) -> ProviderProfile:
        client_id = get_or_throw(self.GOOGLE_CLIENT_ID)
        try:
            payload = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                client_id,
            )
        except ValueError as error:
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

    def _verify_facebook_token(self, token: str) -> ProviderProfile:
        app_id = get_or_throw(self.FACEBOOK_APP_ID)
        app_secret = get_or_throw(self.FACEBOOK_APP_SECRET)
        app_access_token = f"{app_id}|{app_secret}"

        debug_payload = self._get_json(
            f"{self.FACEBOOK_GRAPH_URL}/debug_token",
            {
                "input_token": token,
                "access_token": app_access_token,
            },
        )
        token_data = debug_payload.get("data", {})

        if not token_data.get("is_valid") or str(token_data.get("app_id")) != app_id:
            raise ValueError("Token de Facebook inválido.")

        profile_payload = self._get_json(
            f"{self.FACEBOOK_GRAPH_URL}/me",
            {
                "fields": "id,email,first_name,last_name",
                "access_token": token,
            },
        )

        email = str(profile_payload.get("email") or "").strip().lower()
        provider_user_id = str(profile_payload.get("id") or "").strip()

        if not email or not provider_user_id:
            raise ValueError("La cuenta de Facebook no devolvió email.")

        return ProviderProfile(
            provider=AuthProvider.FACEBOOK,
            provider_user_id=provider_user_id,
            email=email,
            email_verified=True,
            firstname=profile_payload.get("first_name"),
            lastname=profile_payload.get("last_name"),
        )

    def _get_json(self, url: str, params: dict[str, str]) -> dict[str, Any]:
        request_url = f"{url}?{urlencode(params)}"

        with urlopen(request_url, timeout=10) as response:
            body = response.read().decode("utf-8")

        payload = json.loads(body)
        if not isinstance(payload, dict):
            raise ValueError("Respuesta inválida del proveedor.")

        return payload

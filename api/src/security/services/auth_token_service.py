import time
from typing import Any

from flask import current_app, has_app_context
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from auth.enums.auth_enums import AuthProvider
from tools.config_tools import get_or_throw
from users.models.user_model import UserModel


class AuthTokenService:
    ENV_SECRET_KEY = "AUTH_TOKEN_SECRET"
    SALT = "auth-token"
    DEFAULT_MAX_AGE_SECONDS = 3600

    def __init__(
        self,
        secret_key: str | None = None,
        max_age_seconds: int = DEFAULT_MAX_AGE_SECONDS,
    ):
        self.secret_key = secret_key or self._resolve_secret_key()
        self.max_age_seconds = max_age_seconds
        self.serializer = URLSafeTimedSerializer(
            self.secret_key,
            salt=self.SALT,
        )

    def generate_token(self, user: UserModel, auth_provider: AuthProvider) -> str:
        payload = {
            "sub": str(user.id),
            "email": str(user.email),
            "auth_provider": auth_provider.value,
            "iat": int(time.time()),
        }
        return self.serializer.dumps(payload)

    def verify_token(self, token: str) -> dict[str, Any]:
        try:
            payload = self.serializer.loads(token, max_age=self.max_age_seconds)
        except SignatureExpired as error:
            raise ValueError("El token expiró.") from error
        except BadSignature as error:
            raise ValueError("El token no es válido.") from error

        if not isinstance(payload, dict):
            raise ValueError("El token no es válido.")

        return payload

    def _resolve_secret_key(self) -> str:
        try:
            secret_key = get_or_throw(self.ENV_SECRET_KEY).strip()
            if secret_key:
                return secret_key
        except RuntimeError:
            pass

        if has_app_context():
            secret_key = str(current_app.config.get("SECRET_KEY") or "").strip()
            if secret_key:
                return secret_key

        raise RuntimeError(
            f"{self.ENV_SECRET_KEY} o Flask SECRET_KEY debe estar configurada."
        )

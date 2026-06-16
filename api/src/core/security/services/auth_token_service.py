import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from identity.auth.enums.auth_enums import AuthProvider
from core.tools.config_tools import get_or_throw
from identity.users.models.user_model import UserModel


class AuthTokenService:
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    ALGORITHM = "HS256"

    def __init__(self, secret_key: str | None = None, redis=None):
        self.secret_key = secret_key or get_or_throw("AUTH_TOKEN_SECRET")
        self._redis = redis

    @property
    def redis(self):
        if self._redis is None:
            from core.database.redis import redis_client
            self._redis = redis_client
        return self._redis

    def generate_access_token(self, user: UserModel, auth_provider: AuthProvider) -> str:
        from core.config.logger import logger
        logger.debug("[token] generate_access | user_id=%d provider=%s", user.id, auth_provider.value)
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {
                "sub": str(user.id),
                "email": str(user.email),
                "auth_provider": auth_provider.value,
                "iat": now,
                "exp": now + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES),
            },
            self.secret_key,
            algorithm=self.ALGORITHM,
        )
        return token

    async def generate_refresh_token(self, user_id: int) -> str:
        jti = secrets.token_urlsafe(32)
        token = jwt.encode(
            {
                "sub": str(user_id),
                "jti": jti,
                "exp": datetime.now(timezone.utc) + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS),
            },
            self.secret_key,
            algorithm=self.ALGORITHM,
        )
        await self.redis.set(f"refresh:{user_id}", jti, self.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
        return token

    def verify_access_token(self, token: str) -> dict[str, Any]:
        from core.config.logger import logger
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.ALGORITHM])
            logger.debug("[token] verify_access | result=ok user_id=%s", payload.get("sub"))
            return payload
        except jwt.ExpiredSignatureError as e:
            logger.debug("[token] verify_access | result=expired")
            raise ValueError("El token expiró.") from e
        except jwt.InvalidTokenError as e:
            logger.debug("[token] verify_access | result=invalid error=%s", type(e).__name__)
            raise ValueError("El token no es válido.") from e

    async def verify_refresh_token(self, user_id: int, jti: str) -> bool:
        stored = await self.redis.get(f"refresh:{user_id}")
        return stored == jti

    async def revoke_refresh_token(self, user_id: int) -> None:
        await self.redis.delete(f"refresh:{user_id}")

    def verify_token(self, token: str) -> dict[str, Any]:
        return self.verify_access_token(token)

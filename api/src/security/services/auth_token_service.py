import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from auth.enums.auth_enums import AuthProvider
from tools.config_tools import get_or_throw
from users.models.user_model import UserModel


class AuthTokenService:
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    ALGORITHM = "HS256"

    def __init__(self, secret_key: str | None = None, redis=None):
        self.secret_key = secret_key or get_or_throw("AUTH_TOKEN_SECRET")
        self._redis = redis

    @property
    def redis(self):
        if self._redis is None:
            from database.redis import redis_client
            self._redis = redis_client
        return self._redis

    def generate_access_token(self, user: UserModel, auth_provider: AuthProvider) -> str:
        from config.logger import logger
        logger.debug(f"[generate_access_token] START — user_id={user.id} provider={auth_provider.value} secret_prefix={self.secret_key[:6]!r}")
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
        logger.debug(f"[generate_access_token] END   — token_prefix={token[:30]!r}")
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
        from config.logger import logger
        logger.debug(f"[verify_access_token] START — token_prefix={token[:30]!r} secret_prefix={self.secret_key[:6]!r}")
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.ALGORITHM])
            logger.debug(f"[verify_access_token] END   — OK sub={payload.get('sub')}")
            return payload
        except jwt.ExpiredSignatureError as e:
            logger.debug(f"[verify_access_token] END   — EXPIRED")
            raise ValueError("El token expiró.") from e
        except jwt.InvalidTokenError as e:
            logger.debug(f"[verify_access_token] END   — INVALID: {type(e).__name__}: {e}")
            raise ValueError("El token no es válido.") from e

    async def verify_refresh_token(self, user_id: int, jti: str) -> bool:
        stored = await self.redis.get(f"refresh:{user_id}")
        return stored == jti

    async def revoke_refresh_token(self, user_id: int) -> None:
        await self.redis.delete(f"refresh:{user_id}")

    def verify_token(self, token: str) -> dict[str, Any]:
        return self.verify_access_token(token)

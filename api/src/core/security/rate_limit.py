from fastapi import HTTPException, Request, status

from core.database.redis import redis_client


def rate_limit(key_prefix: str, max_attempts: int, window_seconds: int):
    """Dependencia de FastAPI: limita a `max_attempts` requests por IP dentro de
    `window_seconds`. Pensada para endpoints públicos sensibles a fuerza bruta
    (login, registro, forgot-password, verificación de OTP) que hoy no tienen
    ningún límite de intentos."""

    async def _check(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:{key_prefix}:{client_ip}"
        attempts = await redis_client.increment(key, window_seconds)
        if attempts > max_attempts:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiados intentos. Espera un momento antes de volver a intentarlo.",
            )

    return _check

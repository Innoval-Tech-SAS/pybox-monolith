from fastapi import Response

from core.security.constants.cookie_constants import (
    ACCESS_TOKEN_COOKIE,
    REFRESH_TOKEN_COOKIE,
    REFRESH_TOKEN_PATH,
)
from core.security.services.auth_token_service import AuthTokenService
from core.tools.config_tools import get_or_throw


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    secure = True
    domain = get_or_throw("COOKIE_DOMAIN")

    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        max_age=AuthTokenService.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=domain,
        secure=secure,
        httponly=True,
        samesite="lax",
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        max_age=AuthTokenService.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path=REFRESH_TOKEN_PATH,
        domain=domain,
        secure=secure,
        httponly=True,
        samesite="lax",
    )


def clear_auth_cookies(response: Response) -> None:
    domain = get_or_throw("COOKIE_DOMAIN")
    response.delete_cookie(key=ACCESS_TOKEN_COOKIE, path="/", domain=domain)
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE, path=REFRESH_TOKEN_PATH, domain=domain
    )

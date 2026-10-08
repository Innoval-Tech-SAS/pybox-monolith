"""Hashing y verificación de contraseñas con Argon2, con rehash transparente."""

from __future__ import annotations

import base64
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from core.tools.config_tools import get_or_throw


def _b64d_url(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


class PasswordHasherService:
    ENV_PEPPER = "PASSWORD_PEPPER"

    def __init__(
        self,
        ph: Optional[PasswordHasher] = None,
        pepper: Optional[bytes] = None,
    ):
        self._ph = ph or PasswordHasher()

        if pepper is None:
            raw = get_or_throw(self.ENV_PEPPER).strip()
            pepper = _b64d_url(raw) if raw else b""

        self._pepper = pepper

    def _mix(self, password: str) -> str:
        if not self._pepper:
            return password
        return password + self._pepper.decode("utf-8", errors="ignore")

    def hash_password(self, password: str) -> str:
        if not password:
            raise ValueError("La contraseña no puede estar vacía.")
        return self._ph.hash(self._mix(password))

    def verify_password(self, stored_hash: str, password: str) -> bool:
        try:
            return self._ph.verify(stored_hash, self._mix(password))
        except InvalidHashError, VerifyMismatchError:
            return False

    def verify_and_maybe_rehash(
        self,
        stored_hash: str,
        password: str,
    ) -> tuple[bool, str | None]:
        try:
            is_valid = self._ph.verify(stored_hash, self._mix(password))
        except InvalidHashError, VerifyMismatchError:
            return False, None

        if is_valid and self._ph.check_needs_rehash(stored_hash):
            return True, self.hash_password(password)

        return is_valid, None

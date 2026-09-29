from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from core.tools.config_tools import get_or_throw


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64d(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


class EncryptService:
    VERSION = "v1"
    ENCRYPT_KEY = "ENCRYPT_KEY"

    def __init__(self, key: Optional[bytes] = None, hash_key: Optional[bytes] = None):
        if key is None:
            raw = get_or_throw(self.ENCRYPT_KEY)
            key = _b64d(raw)

        if len(key) != 32:
            raise ValueError("La clave debe tener 32 bytes (AES-256).")

        self._aes = AESGCM(key)
        self._hash_key = hash_key or _b64d(get_or_throw("DOCUMENT_HASH_KEY"))

    def _encrypt(self, data: bytes | str, *, aad: Optional[bytes | str] = None) -> str:
        try:
            if isinstance(data, str):
                data = data.encode("utf-8")
            if isinstance(aad, str):
                aad = aad.encode("utf-8")

            nonce = secrets.token_bytes(12)
            ct_and_tag = self._aes.encrypt(nonce, data, aad)
            ciphertext, tag = ct_and_tag[:-16], ct_and_tag[-16:]

            return ":".join(
                [
                    self.VERSION,
                    _b64e(nonce),
                    _b64e(ciphertext),
                    _b64e(tag),
                ]
            )
        except Exception as error:
            raise ValueError(f"Error durante el cifrado: {error}") from error

    def _decrypt(self, token: str, *, aad: Optional[bytes | str] = None) -> bytes:
        if isinstance(aad, str):
            aad = aad.encode("utf-8")

        try:
            version, nonce_b64, ciphertext_b64, tag_b64 = token.split(":")
            if version != self.VERSION:
                raise ValueError("Versión de token desconocida.")
            nonce = _b64d(nonce_b64)
            ciphertext = _b64d(ciphertext_b64)
            tag = _b64d(tag_b64)
        except Exception as error:
            raise ValueError(f"Token inválido: {error}") from error

        return self._aes.decrypt(nonce, ciphertext + tag, aad)

    def encrypt_to_str(self, value: str, **kwargs) -> str:
        return self._encrypt(value, **kwargs)

    def decrypt_to_str(self, token: str, **kwargs) -> str:
        return self._decrypt(token, **kwargs).decode("utf-8")

    def hash_document(self, value: str) -> str:
        return hmac.new(
            self._hash_key, value.encode("utf-8"), hashlib.sha256
        ).hexdigest()


encrypt_service = EncryptService()

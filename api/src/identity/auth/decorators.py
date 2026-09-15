from functools import wraps
from typing import Callable

from flask import g, jsonify, request

from core.security.services.auth_token_service import AuthTokenService

_token_service = AuthTokenService()


def login_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token de acceso requerido."}), 401

        token = auth_header[len("Bearer "):]
        try:
            g.token_payload = _token_service.verify_token(token)
        except ValueError as error:
            return jsonify({"error": str(error)}), 401

        return f(*args, **kwargs)

    return decorated

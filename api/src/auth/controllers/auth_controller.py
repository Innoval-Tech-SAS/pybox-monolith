from flask import Blueprint, request, jsonify

from ..services.auth_service import AuthService
from ..schemas.auth_schemas import ProviderLogin, UserCreate, UserLogin

auth_bp = Blueprint("auth", __name__)

service = AuthService()


@auth_bp.route("/register", methods=["POST"])
def register():
    body: UserCreate = request.get_json(force=True)
    user = service.register_user(body)
    return jsonify({"id": str(user.id), "email": str(user.email)}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    body: UserLogin = request.get_json(force=True)
    result = service.authenticate_user(body)
    return jsonify({
        "access_token": result["access_token"],
        "token_type": result["token_type"],
        "auth_provider": result["auth_provider"].value,
    }), 200


@auth_bp.route("/oauth", methods=["POST"])
def oauth_login():
    body: ProviderLogin = request.get_json(force=True)
    result = service.authenticate_provider_user(body)
    return jsonify({
        "access_token": result["access_token"],
        "token_type": result["token_type"],
        "auth_provider": result["auth_provider"].value,
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    service.close_session()
    return jsonify({"message": "Sesión cerrada."}), 200

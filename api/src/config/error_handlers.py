from flask import Flask, jsonify
from flask.typing import ResponseReturnValue
from werkzeug.exceptions import HTTPException

from contacts.utils.contact_exceptions import DuplicateContactError


def register_error_handlers(app: Flask) -> None:

    @app.errorhandler(DuplicateContactError)
    def handle_duplicate_contact(error: DuplicateContactError) -> ResponseReturnValue:
        return (
            jsonify(
                {
                    "error": str(error),
                    "suggestion": error.suggestion,
                }
            ),
            409,
        )

    @app.errorhandler(ValueError)
    @app.errorhandler(RuntimeError)
    def handle_bad_request(error: Exception) -> ResponseReturnValue:
        return jsonify({"error": str(error)}), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException) -> ResponseReturnValue:
        status_code = error.code or 500
        return jsonify({"error": error.description}), status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> ResponseReturnValue:
        return jsonify({"error": "Error interno del servidor"}), 500

"""Traducción de nombres de campo y tipos de error de Pydantic a mensajes en español."""

FIELD_NAMES: dict[str, str] = {
    "email": "correo electrónico",
    "password": "contraseña",
    "current_password": "contraseña actual",
    "new_password": "nueva contraseña",
    "phone_number": "número de teléfono",
    "firstname": "nombre",
    "lastname": "apellido",
    "document_type": "tipo de documento",
    "document_number": "número de documento",
    "nationality": "nacionalidad",
    "channel": "canal",
    "code": "código",
    "provider": "proveedor",
    "token": "token",
    "refresh_token": "token de actualización",
}

ERROR_MESSAGES: dict[str, str] = {
    "missing": "El campo {field} es obligatorio.",
    "string_type": "El campo {field} debe ser texto.",
    "string_too_short": "El campo {field} es demasiado corto.",
    "string_too_long": "El campo {field} es demasiado largo.",
    "int_type": "El campo {field} debe ser un número entero.",
    "float_type": "El campo {field} debe ser un número.",
    "bool_type": "El campo {field} debe ser verdadero o falso.",
    "enum": "El valor de {field} no está permitido.",
    "url_type": "El campo {field} debe ser una URL válida.",
    "json_invalid": "El cuerpo de la solicitud contiene JSON inválido.",
}

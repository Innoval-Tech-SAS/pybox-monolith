from math import ceil
from typing import Any

from messaging.constants.nrs360_constants import (
    GSM_03_38_CHARSET,
    GSM_03_38_EXTENSION_CHARSET,
    GSM_CONCAT_PART_LENGTH,
    GSM_SINGLE_PART_LENGTH,
    SMS_ENCODING_GSM,
    SMS_ENCODING_UTF16,
    SMS_MAX_PARTS,
    UTF16_CONCAT_PART_LENGTH,
    UTF16_SINGLE_PART_LENGTH,
)


def is_gsm_encodable(text: str) -> bool:
    return all(char in GSM_03_38_CHARSET for char in text)


def _sub_values(sub: list[dict[str, Any]] | None) -> list[tuple[str, str]]:
    return [(key, str(value)) for element in sub or [] for key, value in element.items()]


def resolve_sms_encoding(message: str, sub: list[dict[str, Any]] | None = None) -> str:
    """Elige el ``encoding`` de 360nrs mínimo que renderiza el mensaje sin pérdida.

    Se evalúan tanto la plantilla como los valores del ``sub`` porque la sustitución la
    resuelve 360nrs de su lado: el ``encoding`` aplica al mensaje ya renderizado, así que
    un deudor llamado "María" rompe una plantilla que por sí sola era GSM-safe. La doc no
    especifica si el charset se evalúa antes o después de sustituir, así que se asume el
    caso conservador (después); si fuera antes, el único costo es elegir ``utf-16`` de más.

    Se prefiere ``gsm`` (160 caracteres por parte) sobre ``utf-16`` (70) para no
    multiplicar el costo del envío cuando no hace falta.
    """
    if not is_gsm_encodable(message):
        return SMS_ENCODING_UTF16
    for _, value in _sub_values(sub):
        if not is_gsm_encodable(value):
            return SMS_ENCODING_UTF16
    return SMS_ENCODING_GSM


def measure_length(text: str, encoding: str) -> int:
    """Longitud del texto en las unidades que factura 360nrs para ese ``encoding``.

    En GSM7 los caracteres de la tabla de extensión (``^{}\\[~]|€``) ocupan dos posiciones
    porque viajan precedidos de un ESC. En UCS2 se cuentan unidades UTF-16, de modo que un
    carácter fuera del BMP (emoji) cuenta como dos.
    """
    if encoding == SMS_ENCODING_GSM:
        return sum(2 if char in GSM_03_38_EXTENSION_CHARSET else 1 for char in text)
    return len(text.encode("utf-16-le")) // 2


def render_worst_case(message: str, sub: list[dict[str, Any]] | None, encoding: str) -> str:
    """Sustituye cada variable por su valor más largo del ``sub``.

    El ``parts`` es único para toda la llamada, pero el ``sub`` lleva un valor distinto por
    destinatario y 360nrs sustituye de su lado. Hay que dimensionar contra el destinatario
    más largo del lote: si se calcula con uno corto, el de nombre largo se pasa de partes y
    falla con error 105.
    """
    longest: dict[str, str] = {}
    for key, value in _sub_values(sub):
        if measure_length(value, encoding) > measure_length(longest.get(key, ""), encoding):
            longest[key] = value
    rendered = message
    for key, value in longest.items():
        rendered = rendered.replace("{" + key + "}", value)
    return rendered


def resolve_sms_parts(message: str, sub: list[dict[str, Any]] | None, encoding: str) -> int:
    """Calcula el ``parts`` que necesita el mensaje ya renderizado, acotado al máximo de 360nrs."""
    length = measure_length(render_worst_case(message, sub, encoding), encoding)
    if encoding == SMS_ENCODING_GSM:
        single, concat = GSM_SINGLE_PART_LENGTH, GSM_CONCAT_PART_LENGTH
    else:
        single, concat = UTF16_SINGLE_PART_LENGTH, UTF16_CONCAT_PART_LENGTH
    parts = 1 if length <= single else ceil(length / concat)
    return min(parts, SMS_MAX_PARTS)

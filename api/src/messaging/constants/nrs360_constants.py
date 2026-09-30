"""Endpoints y límites de longitud/partes de la API de 360NRS (SMS/Email)."""

SMS_ENDPOINT = "/sms"
EMAIL_ENDPOINT = "/mailing"

SMS_ENCODING_GSM = "gsm"
SMS_ENCODING_UTF16 = "utf-16"

# Límites de longitud por parte según 360nrs. Un mensaje que entra en una sola parte
# admite el máximo "single"; al concatenarse, cada parte pierde espacio por el header
# de concatenación (UDH) y baja al máximo "concat".
GSM_SINGLE_PART_LENGTH = 160
GSM_CONCAT_PART_LENGTH = 153
UTF16_SINGLE_PART_LENGTH = 70
UTF16_CONCAT_PART_LENGTH = 67

# ``parts`` es el máximo de partes en que 360nrs puede dividir el mensaje.
# Su default es 1 y, si el texto necesita más de las declaradas, el envío
# falla con error 105 (no se trunca). Por eso hay que declararlo
# explícitamente en vez de confiar en el default.
SMS_MAX_PARTS = 15

# Alfabeto GSM 7 bit por defecto (3GPP TS 23.038): tabla básica + tabla de extensión.
# 360nrs usa ``gsm`` cuando no se manda ``encoding``, y sustituye por "?" todo lo que
# caiga fuera de este set. Incluye ``ñ`` y los acentos graves, pero NO ``á í ó ú``,
# que es lo que rompía los mensajes de campaña ("está" -> "est?").
GSM_03_38_EXTENSION_CHARSET = frozenset("\f^{}\\[~]|€")

GSM_03_38_CHARSET = (
    frozenset(
        "@£$¥èéùìòÇ\nØø\rÅå"
        "Δ_ΦΓΛΩΠΨΣΘΞÆæßÉ"
        " !\"#¤%&'()*+,-./"
        "0123456789:;<=>?"
        "¡ABCDEFGHIJKLMNO"
        "PQRSTUVWXYZÄÖÑÜ§"
        "¿abcdefghijklmno"
        "pqrstuvwxyzäöñüà"
    )
    | GSM_03_38_EXTENSION_CHARSET
)

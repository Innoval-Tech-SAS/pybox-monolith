from enum import StrEnum


class ChannelName(StrEnum):
    SMS = "SMS"
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    CALL = "CALL"
    CALL_IA = "CALL_IA"


class Currency(StrEnum):
    """Moneda en la que se costea un canal. USD es la de referencia real — todos los
    canales sembrados (`core/seed/seed_channels.py`) usan USD, porque el proveedor
    (360NRS, WhatsApp Cloud) cobra internacional — y se convierte a la moneda de
    facturación del país al armar la factura (`billing_cron_service.get_usd_rate`).

    Las demás son las 5 monedas locales reales del sistema, una por cada país de
    `Nationality` (`app_platform.countries.enums.country_enums`), para permitir
    costear un canal directo en moneda local si hiciera falta. No incluye monedas de
    países que el sistema no opera (antes tenía EUR, sin ningún uso real)."""

    USD = "USD"
    COP = "COP"  # Colombia
    MXN = "MXN"  # México
    ARS = "ARS"  # Argentina
    PEN = "PEN"  # Perú
    VES = "VES"  # Venezuela

from messaging.campaigns.enums.campaign_enums import Periodicity

PERIODICITY_LABELS: dict[Periodicity, str] = {
    Periodicity.IMMEDIATE: "Inmediato",
    Periodicity.ONCE: "Una vez",
    Periodicity.DAILY: "Diaria",
    Periodicity.WEEKLY: "Semanal",
    Periodicity.MONTHLY: "Mensual",
}

# (valor, etiqueta, activo). Domingo queda inactivo: no se agendan campañas ese día.
WEEKDAYS: list[tuple[int, str, bool]] = [
    (0, "Domingo", False),
    (1, "Lunes", True),
    (2, "Martes", True),
    (3, "Miércoles", True),
    (4, "Jueves", True),
    (5, "Viernes", True),
    (6, "Sábado", True),
]

INACTIVE_WEEKDAYS: set[int] = {value for value, _, active in WEEKDAYS if not active}

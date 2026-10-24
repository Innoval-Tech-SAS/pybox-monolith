"""Tablas fuente y estrategias de variable de personalización de campañas."""

DEBTOR_TABLE = "deudores"
CREDIT_TABLE = "creditos"
PAYMENT_TABLE = "pagos"

# Un crédito tiene muchas cuotas (pagos 1:N) — a diferencia de deudor→crédito (1:1,
# "el crédito vigente"), una variable de pago necesita saber A CUÁL cuota se refiere.
# Se resuelve exponiendo 3 variantes por columna de `pagos` (sufijo en la clave de la
# variable, ej. "monto_pago_proxima_cuota"), en vez de una casilla de selección aparte:
# elegir la variable de la lista YA implica elegir la estrategia.
PAYMENT_STRATEGY_SUFFIXES: dict[str, str] = {
    "proxima_cuota": "Próxima cuota a vencer",
    "primera_vencida": "Primera cuota vencida",
    "ultima_sin_pagar": "Última cuota sin pagar",
}

from app_platform.schema_manager.services.inspector_service import InspectorService
from messaging.campaigns.constants import PAYMENT_STRATEGY_SUFFIXES, PAYMENT_TABLE
from messaging.templates.schemas.template_schemas import TemplateVariableOption
from messaging.templates.utils.template_variable_builder import build_payment_variable, build_variable

_SCHEMA = "public"
_SOURCE_TABLES = ("deudores", "creditos")


class TemplateVariableService:

    def __init__(self, inspector: InspectorService) -> None:
        self._inspector = inspector

    async def list_available_variables(self) -> list[TemplateVariableOption]:
        variables: dict[str, TemplateVariableOption] = {}
        for table in _SOURCE_TABLES:
            fields = await self._inspector.get_table_fields(_SCHEMA, table)
            for field in fields:
                variable = build_variable(field["name"], field["type"], table)
                if variable is not None and variable.key not in variables:
                    variables[variable.key] = variable

        # `pagos` es 1:N por crédito (cronograma de cuotas) — cada columna genera una
        # variable por estrategia de resolución (próxima/vencida/última sin pagar), en
        # vez de una sola variable ambigua (ver PAYMENT_STRATEGY_SUFFIXES).
        payment_fields = await self._inspector.get_table_fields(_SCHEMA, PAYMENT_TABLE)
        for field in payment_fields:
            for suffix, strategy_label in PAYMENT_STRATEGY_SUFFIXES.items():
                variable = build_payment_variable(
                    field["name"], field["type"], suffix, strategy_label, PAYMENT_TABLE
                )
                if variable is not None:
                    variables[variable.key] = variable

        return sorted(variables.values(), key=lambda v: v.key)

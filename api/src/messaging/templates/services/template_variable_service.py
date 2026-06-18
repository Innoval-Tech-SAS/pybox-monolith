from app_platform.schema_manager.services.inspector_service import InspectorService
from messaging.templates.schemas.template_schemas import TemplateVariableOption
from messaging.templates.utils.template_variable_builder import build_variable

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
                variable = build_variable(field["name"], field["type"])
                if variable is not None and variable.key not in variables:
                    variables[variable.key] = variable
        return sorted(variables.values(), key=lambda v: v.key)

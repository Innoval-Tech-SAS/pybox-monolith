import re
from typing import Any

_VAR_PATTERN = re.compile(r"\{(\w+)\}")


class TemplateRenderer:
    """
    Renders templates using NRS360-compatible single-brace syntax: {variable_name}.
    Used exclusively for the /preview endpoint (local substitution for testing).
    The /send endpoint delegates substitution to NRS360 via the sub parameter.
    """

    def __new__(cls) -> "TemplateRenderer":
        if not hasattr(cls, "_instance"):
            cls._instance = super(TemplateRenderer, cls).__new__(cls)
        return cls._instance

    def find_variables(self, source: str) -> set[str]:
        return set(_VAR_PATTERN.findall(source))

    def render(self, source: str, variables: dict[str, Any]) -> str:
        def replace(match: re.Match) -> str:
            return str(variables.get(match.group(1), match.group(0)))

        return _VAR_PATTERN.sub(replace, source)

    def render_fields(
        self,
        body: str,
        subject: str | None,
        variables: dict[str, Any],
    ) -> tuple[str, str]:
        return self.render(body, variables), self.render(subject or "", variables)

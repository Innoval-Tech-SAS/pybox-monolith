"""Resultado interno del procesamiento de una carga masiva de portafolio."""

import uuid
from dataclasses import dataclass, field


@dataclass
class CsvProcessResult:
    total_rows: int
    processed_rows: int
    failed_rows: int
    portfolio_id: uuid.UUID
    titulares: int
    codeudores: int
    creditos: int
    clientes_unicos: int
    errors: list[str] = field(default_factory=list)


@dataclass
class InstallmentsUploadResult:
    total_rows: int
    processed_rows: int
    failed_rows: int
    portfolio_id: uuid.UUID
    cuotas_creadas: int
    cuotas_actualizadas: int
    creditos_liquidados: int
    errors: list[str] = field(default_factory=list)

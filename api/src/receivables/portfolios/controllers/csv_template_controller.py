"""Plantillas CSV descargables — solo el encabezado, para que el usuario sepa qué
columnas debe traer el archivo antes de armarlo. Sin datos sensibles, así que quedan
públicas (mismo criterio que el catálogo de países): no necesitan sesión.
"""

import csv
import io

from fastapi import Response

from core.config.api_router import APIRouter
from receivables.portfolios.constants.portfolio_csv_constants import (
    INSTALLMENT_TEMPLATE_COLUMNS,
    PORTFOLIO_TEMPLATE_COLUMNS,
)

router = APIRouter(prefix="/portfolios", tags=["Plantillas CSV"])


def _csv_header_response(columns: list[str], filename: str) -> Response:
    buffer = io.StringIO()
    csv.writer(buffer).writerow(columns)
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/upload-csv/template",
    summary="Descargar plantilla CSV de portafolio",
    description=(
        "Encabezado del CSV que esperan /upload-csv, /upload-csv/append y "
        "/upload-csv/update."
    ),
)
async def download_portfolio_template() -> Response:
    return _csv_header_response(PORTFOLIO_TEMPLATE_COLUMNS, "plantilla_portafolio.csv")


@router.get(
    "/upload-csv/installments/template",
    summary="Descargar plantilla CSV de plan de cuotas",
    description="Encabezado del CSV que espera /upload-csv/installments.",
)
async def download_installments_template() -> Response:
    return _csv_header_response(
        INSTALLMENT_TEMPLATE_COLUMNS, "plantilla_plan_cuotas.csv"
    )

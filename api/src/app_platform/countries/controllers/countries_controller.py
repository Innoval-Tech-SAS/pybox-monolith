from app_platform.countries.dependencies import CountryServiceDep
from app_platform.countries.schemas.countries_schemas import (
    DocumentTypesResponse,
    NationalityOption,
)
from core.config.api_router import APIRouter

router = APIRouter(prefix="/countries", tags=["Países"])


@router.get(
    "",
    response_model=list[NationalityOption],
    summary="Listar países disponibles",
    description=(
        "Retorna los países soportados (desde base de datos) con sus tipos de "
        "documento, prefijo telefónico y bandera."
    ),
)
async def get_countries(country_service: CountryServiceDep) -> list[NationalityOption]:
    return await country_service.list_countries()


@router.get(
    "/document-types",
    response_model=DocumentTypesResponse,
    summary="Tipos de documento (labels + grupos por país)",
    description=(
        "Labels código→etiqueta y grupos de documentos de persona por país, "
        "desde DB. Reemplaza el dict estático del frontend."
    ),
)
async def get_document_types(
    country_service: CountryServiceDep,
) -> DocumentTypesResponse:
    return await country_service.get_document_types()

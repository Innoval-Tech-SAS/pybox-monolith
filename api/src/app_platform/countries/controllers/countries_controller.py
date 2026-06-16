from core.config.api_router import APIRouter

from app_platform.countries.schemas.countries_schemas import NationalityOption
from app_platform.countries.enums.country_enums import DOCUMENTS_BY_NATIONALITY, NATIONALITY_NAMES, NATIONALITY_PHONE_PREFIX, Nationality

router = APIRouter(prefix="/countries", tags=["Países"])


@router.get(
    "",
    response_model=list[NationalityOption],
    summary="Listar países disponibles",
    description="Retorna los países soportados con sus tipos de documento, prefijo telefónico y bandera.",
)
async def get_countries() -> list[NationalityOption]:
    return [
        NationalityOption(
            code=n.value,
            name=NATIONALITY_NAMES[n],
            flag_url=f"https://flagcdn.com/{n.value.lower()}.svg",
            phone_prefix=NATIONALITY_PHONE_PREFIX[n],
            document_types=[d.value for d in DOCUMENTS_BY_NATIONALITY[n]],
        )
        for n in Nationality
    ]

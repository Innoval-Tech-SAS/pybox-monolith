from config.api_router import APIRouter

from countries.schemas.countries_schemas import NationalityOption
from countries.enums.country_enums import DOCUMENTS_BY_NATIONALITY, NATIONALITY_NAMES, NATIONALITY_PHONE_PREFIX, Nationality

router = APIRouter(prefix="/countries", tags=["countries"])


@router.get("", response_model=list[NationalityOption])
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

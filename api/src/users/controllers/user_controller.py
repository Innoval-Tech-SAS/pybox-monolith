from config.api_router import APIRouter

from auth.dependencies import TokenPayload
from security.dependencies import CurrentSession
from users.dependencies import UserServiceDep
from users.schemas.user_preferences_schema import UserToursSchema
from users.schemas.user_schemas import UserSummarySchema
from users.schemas.user_session_schema import UserSession, session_key

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSession)
async def me(payload: TokenPayload, service: UserServiceDep) -> UserSession:
    user_id = int(payload["sub"])
    cached = await service.redis.get_json(session_key(user_id), UserSession)
    if cached is not None:
        return cached
    return await service.get_user_session(user_id)


@router.get("/me/preferences/tours", response_model=UserToursSchema)
async def get_tour_preferences(payload: TokenPayload, service: UserServiceDep) -> UserToursSchema:
    user_id = int(payload["sub"])
    dismissed = await service.get_dismissed_tours(user_id)
    return UserToursSchema(dismissed_tours=dismissed)


@router.post("/me/preferences/tours/{tour_key}/dismiss", response_model=UserToursSchema)
async def dismiss_tour(tour_key: str, payload: TokenPayload, service: UserServiceDep) -> UserToursSchema:
    user_id = int(payload["sub"])
    dismissed = await service.dismiss_tour(user_id, tour_key)
    return UserToursSchema(dismissed_tours=dismissed)


@router.get("", response_model=list[UserSummarySchema])
async def list_users(session: CurrentSession, service: UserServiceDep):
    return await service.get_accessible_users(session)

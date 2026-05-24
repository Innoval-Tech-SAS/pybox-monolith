from config.api_router import APIRouter

from auth.dependencies import TokenPayload
from users.dependencies import UserServiceDep
from users.schemas.user_session_schema import UserSession, session_key

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSession)
async def me(payload: TokenPayload, service: UserServiceDep) -> UserSession:
    user_id = int(payload["sub"])
    cached = await service.redis.get_json(session_key(user_id), UserSession)
    if cached is not None:
        return cached
    return await service.get_user_session(user_id)

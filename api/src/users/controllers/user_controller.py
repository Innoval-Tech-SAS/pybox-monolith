from config.api_router import APIRouter
from fastapi import File, HTTPException, Query, UploadFile, status

from auth.dependencies import TokenPayload
from security.dependencies import CurrentSession
from users.dependencies import UserServiceDep
from users.schemas.user_preferences_schema import UserToursSchema
from users.schemas.user_schemas import AdminUserDetailSchema, AdminUserSummarySchema, ChatAvailableUserSchema, ProfilePhotoSchema, UpdateUserSchema
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


@router.put("/me/profile-photo", response_model=ProfilePhotoSchema)
async def update_profile_photo(
    payload: TokenPayload,
    service: UserServiceDep,
    file: UploadFile = File(...),
) -> ProfilePhotoSchema:
    user_id = int(payload["sub"])
    return await service.update_profile_photo(user_id, file)


@router.get("/available-for-chat", response_model=list[ChatAvailableUserSchema])
async def get_available_for_chat(session: CurrentSession, service: UserServiceDep):
    return await service.get_available_for_chat(session)


@router.get("", response_model=list[AdminUserSummarySchema])
async def list_users(session: CurrentSession, service: UserServiceDep, org_id: str | None = Query(None)):
    return await service.get_accessible_users(session, org_id=org_id)


@router.get("/{user_id}", response_model=AdminUserDetailSchema)
async def get_user(user_id: int, service: UserServiceDep):
    return await service.get_user_detail(user_id)


@router.patch("/{user_id}", response_model=AdminUserDetailSchema)
async def update_user(user_id: int, data: UpdateUserSchema, service: UserServiceDep):
    return await service.update_user(user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, payload: TokenPayload, service: UserServiceDep):
    calling_user_id = int(payload["sub"])
    if calling_user_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes eliminarte a ti mismo.")
    await service.soft_delete_user(user_id)

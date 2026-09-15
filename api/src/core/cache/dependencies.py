from typing import Annotated

from fastapi import Depends

from core.cache.cache_service import CacheService, cache_service


def get_cache_service() -> CacheService:
    return cache_service


CacheServiceDep = Annotated[CacheService, Depends(get_cache_service)]

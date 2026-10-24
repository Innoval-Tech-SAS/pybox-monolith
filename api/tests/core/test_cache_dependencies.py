from core.cache.cache_service import CacheService, cache_service
from core.cache.dependencies import get_cache_service


class TestGetCacheService:
    """core/cache/dependencies.py no tenía ni un test (0%): confirma que la
    dependencia expone el singleton compartido `cache_service`, no una instancia
    nueva por request (perdería el propósito de un cache-aside compartido)."""

    def test_returns_cache_service_instance(self):
        result = get_cache_service()
        assert isinstance(result, CacheService)

    def test_returns_shared_singleton(self):
        assert get_cache_service() is cache_service

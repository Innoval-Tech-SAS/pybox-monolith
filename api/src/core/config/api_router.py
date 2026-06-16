from fastapi import APIRouter as _FastAPIRouter


class APIRouter(_FastAPIRouter):
    def add_api_route(self, path: str, endpoint, **kwargs):
        kwargs.setdefault("response_model_by_alias", True)
        super().add_api_route(path, endpoint, **kwargs)

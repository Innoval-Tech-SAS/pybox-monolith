from fastapi import APIRouter as _FastAPIRouter


class APIRouter(_FastAPIRouter):
    def add_api_route(self, path: str, endpoint, **kwargs):
        kwargs.setdefault("response_model_by_alias", True)

        # FastAPI (a diferencia de starlette.routing.Route) no agrega HEAD
        # automáticamente a las rutas GET: `_populate_api_route_state` arma
        # `route.methods` directo desde lo que se le pasa, sin ese fallback.
        # Sin esto, cualquier cliente que sondee con HEAD antes de un GET (p.ej.
        # el visor de documentos, que hace HEAD antes de mostrar el iframe) recibe
        # 405 aunque el endpoint sí sirva GET.
        methods = {m.upper() for m in kwargs.get("methods") or ["GET"]}
        if "GET" in methods:
            methods.add("HEAD")
        kwargs["methods"] = methods

        super().add_api_route(path, endpoint, **kwargs)

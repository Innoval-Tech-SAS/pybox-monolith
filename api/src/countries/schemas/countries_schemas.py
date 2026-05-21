from base.schema_base import BaseSchema


class NationalityOption(BaseSchema):
    code: str
    name: str
    flag_url: str
    phone_prefix: str
    document_types: list[str]

from core.base.schema_base import BaseSchema


class UserToursSchema(BaseSchema):
    dismissed_tours: list[str]

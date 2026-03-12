from ninja import Schema
from typing import Optional


class UserOut(Schema):
    id: int
    email: str
    name: str = ''
    avatar_url: Optional[str] = None

    @staticmethod
    def resolve_name(obj):
        return obj.display_name

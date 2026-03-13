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

    @staticmethod
    def resolve_avatar_url(obj):
        url = obj.avatar_url
        if not url:
            return None
        if not url.startswith(('http://', 'https://')):
            return 'https://' + url
        return url

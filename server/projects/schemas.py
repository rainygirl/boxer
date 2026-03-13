from ninja import Schema
from typing import Optional
from datetime import datetime
from uuid import UUID
from accounts.schemas import UserOut


class ProjectCreate(Schema):
    name: str
    description: str = ''
    color: str = '#6366f1'
    key: Optional[str] = None  # auto-generated if omitted
    visibility: str = 'private'


class ProjectUpdate(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    key: Optional[str] = None
    visibility: Optional[str] = None


class ProjectColumnsUpdate(Schema):
    disabled_statuses: list[str]


class ProjectOut(Schema):
    id: UUID
    name: str
    description: str
    color: str
    key: str
    disabled_statuses: list[str]
    visibility: str
    owner: UserOut
    is_favorite: bool = False
    members: list['ProjectMemberOut'] = []
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_is_favorite(obj) -> bool:
        return bool(getattr(obj, 'is_favorite', False))

    @staticmethod
    def resolve_members(obj) -> list:
        return list(obj.memberships.all())


class ProjectMemberOut(Schema):
    user: UserOut
    role: str


class MemberInvite(Schema):
    email: str


class MemberRoleUpdate(Schema):
    role: str

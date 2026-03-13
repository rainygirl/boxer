from uuid import UUID
from typing import List, Optional
from ninja import Schema


class GitHubIntegrationOut(Schema):
    id: UUID
    repo_owner: str
    repo_name: str
    webhook_secret: str
    is_configured: bool


class GitHubIntegrationUpdate(Schema):
    repo_owner: str = ''
    repo_name: str = ''
    webhook_secret: str = ''


class ProjectWebhookOut(Schema):
    id: UUID
    url: str
    secret: str
    events: List[str]
    active: bool


class ProjectWebhookCreate(Schema):
    url: str
    secret: str = ''
    events: List[str] = []
    active: bool = True


class ProjectWebhookUpdate(Schema):
    url: Optional[str] = None
    secret: Optional[str] = None
    events: Optional[List[str]] = None
    active: Optional[bool] = None

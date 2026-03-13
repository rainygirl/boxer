from typing import List
from uuid import UUID

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from projects.models import Project
from .models import GitHubIntegration, ProjectWebhook
from .schemas import (
    GitHubIntegrationOut,
    GitHubIntegrationUpdate,
    ProjectWebhookOut,
    ProjectWebhookCreate,
    ProjectWebhookUpdate,
)

router = Router()


def _owner_project(project_id: UUID, user) -> Project:
    project = get_object_or_404(Project, pk=project_id, members=user)
    if project.owner != user:
        raise HttpError(403, 'Only project owners can manage integrations')
    return project


# ── GitHub Integration ────────────────────────────────────────────────────────

@router.get('/projects/{project_id}/github', response=GitHubIntegrationOut,
            summary='GitHub 연동 설정 조회')
def get_github(request: HttpRequest, project_id: UUID):
    project = get_object_or_404(Project, pk=project_id, members=request.auth)
    integration, _ = GitHubIntegration.objects.get_or_create(project=project)
    return integration


@router.patch('/projects/{project_id}/github', response=GitHubIntegrationOut,
              summary='GitHub 연동 설정 저장')
def update_github(request: HttpRequest, project_id: UUID, payload: GitHubIntegrationUpdate):
    project = _owner_project(project_id, request.auth)
    integration, _ = GitHubIntegration.objects.get_or_create(project=project)
    integration.repo_owner = payload.repo_owner
    integration.repo_name = payload.repo_name
    integration.webhook_secret = payload.webhook_secret
    integration.save()
    return integration


# ── Outgoing Webhooks ─────────────────────────────────────────────────────────

@router.get('/projects/{project_id}/webhooks', response=List[ProjectWebhookOut],
            summary='Webhook 목록')
def list_webhooks(request: HttpRequest, project_id: UUID):
    project = get_object_or_404(Project, pk=project_id, members=request.auth)
    return project.webhooks.all()


@router.post('/projects/{project_id}/webhooks', response=ProjectWebhookOut,
             summary='Webhook 추가')
def create_webhook(request: HttpRequest, project_id: UUID, payload: ProjectWebhookCreate):
    project = _owner_project(project_id, request.auth)
    return ProjectWebhook.objects.create(
        project=project,
        created_by=request.auth,
        **payload.dict(),
    )


@router.patch('/projects/{project_id}/webhooks/{webhook_id}', response=ProjectWebhookOut,
              summary='Webhook 수정')
def update_webhook(request: HttpRequest, project_id: UUID, webhook_id: UUID,
                   payload: ProjectWebhookUpdate):
    project = _owner_project(project_id, request.auth)
    wh = get_object_or_404(ProjectWebhook, pk=webhook_id, project=project)
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(wh, k, v)
    wh.save()
    return wh


@router.delete('/projects/{project_id}/webhooks/{webhook_id}', summary='Webhook 삭제')
def delete_webhook(request: HttpRequest, project_id: UUID, webhook_id: UUID):
    project = _owner_project(project_id, request.auth)
    wh = get_object_or_404(ProjectWebhook, pk=webhook_id, project=project)
    wh.delete()
    return {'ok': True}

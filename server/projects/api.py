import re
from typing import List
from uuid import UUID
from ninja import Router
from ninja.errors import HttpError
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from .models import Project, ProjectMember, ProjectFavorite
from .schemas import ProjectCreate, ProjectUpdate, ProjectColumnsUpdate, ProjectOut, ProjectMemberOut, MemberInvite, MemberRoleUpdate

_KEY_RE = re.compile(r'^[A-Z]{1,5}$')


def _validate_key(key: str, exclude_id=None) -> str:
    key = key.strip().upper()
    if not _KEY_RE.match(key):
        raise HttpError(400, 'Project key must be 1–5 uppercase letters (A–Z only)')
    qs = Project.objects.filter(key=key)
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    if qs.exists():
        raise HttpError(400, f'Project key "{key}" is already in use')
    return key

User = get_user_model()

router = Router()


def _get_project_for_user(pk: UUID, user) -> Project:
    return get_object_or_404(
        Project,
        pk=pk,
        members=user,
    )


def _annotate_favorites(qs, user):
    fav_sub = ProjectFavorite.objects.filter(project=OuterRef('pk'), user=user)
    return qs.annotate(is_favorite=Exists(fav_sub))


@router.get('', response=List[ProjectOut], summary='내 프로젝트 목록')
def list_projects(request: HttpRequest):
    qs = (
        Project.objects
        .filter(members=request.auth)
        .select_related('owner')
        .prefetch_related('memberships__user')
    )
    return _annotate_favorites(qs, request.auth)


@router.post('', response=ProjectOut, summary='프로젝트 생성')
def create_project(request: HttpRequest, payload: ProjectCreate):
    data = payload.dict(exclude_none=True)
    if 'key' in data:
        data['key'] = _validate_key(data['key'])
    project = Project.objects.create(owner=request.auth, **data)
    ProjectMember.objects.create(project=project, user=request.auth, role='owner')
    return Project.objects.select_related('owner').get(pk=project.pk)


@router.get('/{project_id}', response=ProjectOut, summary='프로젝트 상세')
def get_project(request: HttpRequest, project_id: UUID):
    return _get_project_for_user(project_id, request.auth)


@router.patch('/{project_id}', response=ProjectOut, summary='프로젝트 수정')
def update_project(request: HttpRequest, project_id: UUID, payload: ProjectUpdate):
    project = _get_project_for_user(project_id, request.auth)
    # Only owner can update
    if project.owner != request.auth:
        raise HttpError(403, 'Only the owner can update this project')

    data = payload.dict(exclude_none=True)
    if 'key' in data:
        data['key'] = _validate_key(data['key'], exclude_id=project.pk)
    for k, v in data.items():
        setattr(project, k, v)
    project.save()
    return Project.objects.select_related('owner').get(pk=project.pk)


@router.patch('/{project_id}/columns', response=ProjectOut, summary='컬럼 표시 설정')
def update_project_columns(request: HttpRequest, project_id: UUID, payload: ProjectColumnsUpdate):
    project = _get_project_for_user(project_id, request.auth)
    valid_statuses = {'backlog', 'todo', 'in_progress', 'done', 'confirmed', 'cancelled'}
    project.disabled_statuses = [s for s in payload.disabled_statuses if s in valid_statuses]
    project.save(update_fields=['disabled_statuses'])
    return Project.objects.select_related('owner').get(pk=project.pk)


@router.post('/{project_id}/favorite', summary='즐겨찾기 토글')
def toggle_favorite(request: HttpRequest, project_id: UUID):
    _get_project_for_user(project_id, request.auth)
    fav, created = ProjectFavorite.objects.get_or_create(project_id=project_id, user=request.auth)
    if not created:
        fav.delete()
        return {'favorited': False}
    return {'favorited': True}


@router.delete('/{project_id}', summary='프로젝트 삭제')
def delete_project(request: HttpRequest, project_id: UUID):
    project = _get_project_for_user(project_id, request.auth)
    if project.owner != request.auth:
        raise HttpError(403, 'Only the owner can delete this project')
    project.delete()
    return {'ok': True}


@router.get('/{project_id}/members', response=List[ProjectMemberOut], summary='멤버 목록')
def list_members(request: HttpRequest, project_id: UUID):
    _get_project_for_user(project_id, request.auth)
    return ProjectMember.objects.filter(project_id=project_id).select_related('user')


@router.post('/{project_id}/members', response=ProjectMemberOut, summary='멤버 초대')
def invite_member(request: HttpRequest, project_id: UUID, payload: MemberInvite):
    project = _get_project_for_user(project_id, request.auth)
    if project.owner != request.auth:
        raise HttpError(403, 'Only the owner can invite members')

    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        raise HttpError(404, 'No user found with that email')

    if ProjectMember.objects.filter(project=project, user=user).exists():
        raise HttpError(400, 'User is already a member')

    membership = ProjectMember.objects.create(project=project, user=user, role='member')
    return membership


@router.patch('/{project_id}/members/{user_id}', response=ProjectMemberOut, summary='역할 변경')
def update_member_role(request: HttpRequest, project_id: UUID, user_id: int, payload: MemberRoleUpdate):
    project = _get_project_for_user(project_id, request.auth)
    if project.owner != request.auth:
        raise HttpError(403, 'Only the owner can change roles')

    if payload.role not in ('member', 'viewer'):
        raise HttpError(400, 'Role must be member or viewer')

    membership = get_object_or_404(ProjectMember, project=project, user_id=user_id)
    if membership.role == 'owner':
        raise HttpError(400, 'Cannot change the owner role')

    membership.role = payload.role
    membership.save()
    return membership


@router.delete('/{project_id}/members/{user_id}', summary='멤버 제거')
def remove_member(request: HttpRequest, project_id: UUID, user_id: int):
    project = _get_project_for_user(project_id, request.auth)
    if project.owner != request.auth:
        raise HttpError(403, 'Only the owner can remove members')

    membership = get_object_or_404(ProjectMember, project=project, user_id=user_id)
    if membership.role == 'owner':
        raise HttpError(400, 'Cannot remove the owner')

    membership.delete()
    return {'ok': True}

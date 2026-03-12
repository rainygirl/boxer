import re
from typing import List
from uuid import UUID
from ninja import Router, File
from ninja.files import UploadedFile
from django.conf import settings
from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from ninja.errors import HttpError
from projects.models import Project
from .models import Task, TaskAttachment
from .schemas import TaskCreate, TaskUpdate, TaskMove, TaskOut, AttachmentOut

router = Router()
User = get_user_model()


def _get_project(project_id: UUID, user) -> Project:
    return get_object_or_404(Project, pk=project_id, members=user)


def _get_task(task_id: UUID, project: Project) -> Task:
    return get_object_or_404(Task, pk=task_id, project=project)


def _task_qs():
    return Task.objects.select_related('assignee', 'created_by', 'project')


@router.get('/my', response=List[TaskOut], summary='나에게 할당된 태스크')
def my_tasks(request: HttpRequest):
    return (
        _task_qs()
        .filter(assignee=request.auth, project__members=request.auth)
        .order_by('status', 'sort_order', 'created_at')
    )


@router.get('/project/{project_id}', response=List[TaskOut], summary='프로젝트 태스크 목록')
def list_tasks(request: HttpRequest, project_id: UUID):
    _get_project(project_id, request.auth)
    return _task_qs().filter(project_id=project_id).order_by('sort_order', 'created_at')


@router.post('/project/{project_id}', response=TaskOut, summary='태스크 생성')
def create_task(request: HttpRequest, project_id: UUID, payload: TaskCreate):
    with transaction.atomic():
        project = get_object_or_404(
            Project.objects.select_for_update(), pk=project_id, members=request.auth
        )
        number = project.next_task_number
        project.next_task_number += 1
        project.save(update_fields=['next_task_number'])

        max_order = (
            Task.objects
            .filter(project=project, status=payload.status)
            .order_by('-sort_order')
            .values_list('sort_order', flat=True)
            .first()
        ) or 0

        data = payload.dict()
        assignee_id = data.pop('assignee_id', None)
        task = Task.objects.create(
            project=project,
            created_by=request.auth,
            sort_order=max_order + 1000,
            assignee_id=assignee_id,
            number=number,
            **data,
        )
    return _task_qs().get(pk=task.pk)


@router.get('/{task_id}', response=TaskOut, summary='태스크 상세')
def get_task(request: HttpRequest, task_id: UUID):
    task = get_object_or_404(_task_qs(), pk=task_id)
    _get_project(task.project_id, request.auth)
    return task


@router.patch('/{task_id}', response=TaskOut, summary='태스크 수정')
def update_task(request: HttpRequest, task_id: UUID, payload: TaskUpdate):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)

    data = payload.dict(exclude_none=True)
    for key, value in data.items():
        setattr(task, key, value)
    task.save()
    return _task_qs().get(pk=task.pk)


@router.patch('/{task_id}/move', response=TaskOut, summary='태스크 이동 (칸반 드래그)')
def move_task(request: HttpRequest, task_id: UUID, payload: TaskMove):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)

    with transaction.atomic():
        task.status = payload.status
        task.sort_order = payload.sort_order
        update_fields = ['status', 'sort_order', 'updated_at']

        if payload.project_id and payload.project_id != task.project_id:
            target = get_object_or_404(
                Project.objects.select_for_update(), pk=payload.project_id, members=request.auth
            )
            number = target.next_task_number
            target.next_task_number += 1
            target.save(update_fields=['next_task_number'])

            task.project = target
            task.number = number
            update_fields += ['project', 'number']

        task.save(update_fields=update_fields)

    return _task_qs().get(pk=task.pk)


@router.delete('/{task_id}', summary='태스크 삭제')
def delete_task(request: HttpRequest, task_id: UUID):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)
    task.delete()
    return {'ok': True}


# ── Attachments ──────────────────────────────────────────────────────────────

def _attachment_out(att: TaskAttachment) -> dict:
    from .r2 import get_presigned_url
    return {
        'id': att.id,
        'filename': att.filename,
        'content_type': att.content_type,
        'size': att.size,
        'url': get_presigned_url(att.file_key),
        'uploaded_by': att.uploaded_by,
        'created_at': att.created_at,
    }


@router.get('/{task_id}/attachments', response=List[AttachmentOut], summary='첨부파일 목록')
def list_attachments(request: HttpRequest, task_id: UUID):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)
    atts = task.attachments.select_related('uploaded_by')
    return [_attachment_out(a) for a in atts]


@router.post('/{task_id}/attachments', response=AttachmentOut, summary='첨부파일 업로드')
def upload_attachment(request: HttpRequest, task_id: UUID, file: UploadedFile = File(...)):
    if not settings.R2_CONFIGURED:
        raise HttpError(503, 'File storage is not configured')

    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)

    MAX_SIZE = 50 * 1024 * 1024  # 50 MB
    if file.size and file.size > MAX_SIZE:
        raise HttpError(413, 'File too large (max 50 MB)')

    from .r2 import upload_file
    result = upload_file(file, file.name)

    att = TaskAttachment.objects.create(
        task=task,
        file_key=result['key'],
        filename=file.name,
        content_type=result['content_type'],
        size=result['size'],
        uploaded_by=request.auth,
    )
    att.refresh_from_db()
    att.uploaded_by = request.auth
    return _attachment_out(att)


@router.delete('/{task_id}/attachments/{attachment_id}', summary='첨부파일 삭제')
def delete_attachment(request: HttpRequest, task_id: UUID, attachment_id: UUID):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)
    att = get_object_or_404(TaskAttachment, pk=attachment_id, task=task)
    from .r2 import delete_file
    try:
        delete_file(att.file_key)
    except Exception:
        pass
    att.delete()
    return {'ok': True}

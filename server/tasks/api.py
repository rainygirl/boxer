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
from django.db.models import Prefetch
from projects.models import Project
from .models import Task, TaskAttachment, TaskActivity, TaskDependency, TaskComment, Notification
from .schemas import TaskCreate, TaskUpdate, TaskMove, TaskOut, AttachmentOut, TaskActivityOut, DependencyAddIn, DependenciesOut, DependencyTaskOut, SubTaskCreate, SubTaskUpdate, SubTaskOut, CommentCreate, CommentOut, TaskSearchResult

router = Router()
User = get_user_model()


def _dispatch(project_id, event_type, payload):
    try:
        from integrations.dispatcher import dispatch_webhook
        dispatch_webhook(str(project_id), event_type, payload)
    except Exception:
        pass


def _get_project(project_id: UUID, user) -> Project:
    from django.db.models import Q
    return get_object_or_404(
        Project.objects.filter(Q(members=user) | Q(visibility='public')).distinct(),
        pk=project_id,
    )


def _get_task(task_id: UUID, project: Project) -> Task:
    return get_object_or_404(Task, pk=task_id, project=project)


def _task_qs():
    subtask_qs = Task.objects.select_related('assignee', 'parent_task', 'project').order_by('sub_number')
    return (
        Task.objects
        .select_related('assignee', 'created_by', 'project')
        .prefetch_related(Prefetch('subtasks', queryset=subtask_qs))
    )


@router.get('/my', response=List[TaskOut], summary='나에게 할당된 태스크')
def my_tasks(request: HttpRequest):
    from django.db.models import Q
    accessible = Project.objects.filter(Q(members=request.auth) | Q(visibility='public')).values_list('id', flat=True)
    return (
        _task_qs()
        .filter(assignee=request.auth, project_id__in=accessible, parent_task__isnull=True)
        .order_by('status', 'sort_order', 'created_at')
    )


@router.get('/by-user/{user_id}', response=List[TaskOut], summary='특정 유저 태스크 목록')
def user_tasks(request: HttpRequest, user_id: int):
    target_user = get_object_or_404(User, pk=user_id)
    # Only return tasks in projects accessible to the requester that also include the target
    from django.db.models import Q
    shared_project_ids = (
        Project.objects
        .filter(Q(members=request.auth) | Q(visibility='public'))
        .filter(Q(members=target_user) | Q(visibility='public'))
        .distinct()
        .values_list('id', flat=True)
    )
    return (
        _task_qs()
        .filter(
            assignee=target_user,
            project_id__in=shared_project_ids,
            parent_task__isnull=True,
        )
        .order_by('status', 'sort_order', 'created_at')
    )


@router.get('/search', response=List[TaskSearchResult], summary='태스크 검색')
def search_tasks(request: HttpRequest, q: str = ''):
    if not q.strip():
        return []
    qs = (
        Task.objects
        .select_related('project')
        .filter(project_id__in=Project.objects.filter(Q(members=request.auth) | Q(visibility='public')).values_list('id', flat=True), parent_task__isnull=True)
    )
    # Filter by title or ref (ref is <key>-<number>)
    from django.db.models import Q, Value, CharField
    from django.db.models.functions import Concat
    results = qs.annotate(
        ref_str=Concat('project__key', Value('-'), 'number', output_field=CharField())
    ).filter(
        Q(title__icontains=q) | Q(ref_str__icontains=q)
    ).order_by('-created_at')[:20]
    return list(results)


@router.get('/project/{project_id}', response=List[TaskOut], summary='프로젝트 태스크 목록')
def list_tasks(request: HttpRequest, project_id: UUID):
    _get_project(project_id, request.auth)
    return _task_qs().filter(project_id=project_id, parent_task__isnull=True).order_by('sort_order', 'created_at')


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
        TaskActivity.objects.create(task=task, user=request.auth, activity_type='created', data={})

        if assignee_id:
            assignee = User.objects.filter(pk=assignee_id).first()
            if assignee:
                Notification.objects.create(
                    recipient=assignee,
                    actor=request.auth,
                    type='assigned',
                    task=task,
                )

    result = _task_qs().get(pk=task.pk)
    _dispatch(project.id, 'task.created', {
        'task_id': str(task.id),
        'task_ref': f'{project.key}-{task.number}',
        'task_title': task.title,
        'status': task.status,
        'priority': task.priority,
        'assignee': task.assignee.display_name if task.assignee else None,
    })
    return result


@router.get('/{task_id}', response=TaskOut, summary='태스크 상세')
def get_task(request: HttpRequest, task_id: UUID):
    task = get_object_or_404(_task_qs(), pk=task_id)
    _get_project(task.project_id, request.auth)
    return task


@router.patch('/{task_id}', response=TaskOut, summary='태스크 수정')
def update_task(request: HttpRequest, task_id: UUID, payload: TaskUpdate):
    task = get_object_or_404(Task.objects.select_related('assignee'), pk=task_id)
    _get_project(task.project_id, request.auth)

    data = payload.dict(exclude_unset=True)
    activities = []

    if 'status' in data and data['status'] != task.status:
        activities.append(TaskActivity(
            task=task, user=request.auth, activity_type='status_changed',
            data={'from': task.status, 'to': data['status']},
        ))

    if 'priority' in data and data['priority'] != task.priority:
        activities.append(TaskActivity(
            task=task, user=request.auth, activity_type='priority_changed',
            data={'from': task.priority, 'to': data['priority']},
        ))

    assignee_notification_user = None
    if 'assignee_id' in data:
        old = task.assignee
        new_id = data['assignee_id']
        old_id = old.id if old else None
        if new_id != old_id:
            new_user = User.objects.filter(pk=new_id).first() if new_id else None
            activities.append(TaskActivity(
                task=task, user=request.auth, activity_type='assignee_changed',
                data={
                    'from_id': old_id,
                    'from_name': old.display_name if old else None,
                    'to_id': new_id,
                    'to_name': new_user.display_name if new_user else None,
                },
            ))
            if new_user:
                assignee_notification_user = new_user
        task.assignee_id = data.pop('assignee_id')

    if ('title' in data and data['title'] != task.title) or \
       ('description' in data and data['description'] != task.description):
        activities.append(TaskActivity(
            task=task, user=request.auth, activity_type='content_edited', data={},
        ))

    if 'due_date' in data and str(data['due_date'] or '') != str(task.due_date or ''):
        activities.append(TaskActivity(
            task=task, user=request.auth, activity_type='due_date_changed',
            data={
                'from': str(task.due_date) if task.due_date else None,
                'to': str(data['due_date']) if data['due_date'] else None,
            },
        ))

    for key, value in data.items():
        setattr(task, key, value)
    task.save()

    if activities:
        TaskActivity.objects.bulk_create(activities)

    # Notification: assigned
    if assignee_notification_user:
        Notification.objects.create(
            recipient=assignee_notification_user,
            actor=request.auth,
            type='assigned',
            task=task,
        )

    result = _task_qs().get(pk=task.pk)
    _dispatch(task.project_id, 'task.updated', {
        'task_id': str(task.id),
        'task_ref': f'{task.project.key}-{task.number}',
        'task_title': task.title,
        'changes': list(data.keys()),
    })
    if any(a.activity_type == 'status_changed' for a in activities):
        _dispatch(task.project_id, 'task.status_changed', {
            'task_id': str(task.id),
            'task_ref': f'{task.project.key}-{task.number}',
            'task_title': task.title,
            'status': task.status,
        })
    return result


@router.patch('/{task_id}/move', response=TaskOut, summary='태스크 이동 (칸반 드래그)')
def move_task(request: HttpRequest, task_id: UUID, payload: TaskMove):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)

    with transaction.atomic():
        activities = []
        old_status = task.status  # 변경 전 상태를 먼저 캡처

        if payload.status != old_status:
            activities.append(TaskActivity(
                task=task, user=request.auth, activity_type='status_changed',
                data={'from': old_status, 'to': payload.status},
            ))

        task.status = payload.status
        task.sort_order = payload.sort_order
        update_fields = ['status', 'sort_order', 'updated_at']

        if payload.project_id and payload.project_id != task.project_id:
            target = get_object_or_404(
                Project.objects.select_for_update(), pk=payload.project_id, members=request.auth
            )
            activities.append(TaskActivity(
                task=task, user=request.auth, activity_type='project_moved',
                data={'from_project': task.project.name, 'from_project_id': str(task.project_id), 'to_project': target.name, 'to_project_id': str(target.id)},
            ))
            number = target.next_task_number
            target.next_task_number += 1
            target.save(update_fields=['next_task_number'])

            task.project = target
            task.number = number
            update_fields += ['project', 'number']

        task.save(update_fields=update_fields)

        if activities:
            TaskActivity.objects.bulk_create(activities)

    return _task_qs().get(pk=task.pk)


@router.get('/{task_id}/activities', response=List[TaskActivityOut], summary='태스크 이력')
def list_activities(request: HttpRequest, task_id: UUID):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)
    return task.activities.select_related('user').order_by('-created_at')[:100]


@router.delete('/{task_id}', summary='태스크 삭제')
def delete_task(request: HttpRequest, task_id: UUID):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)
    task.delete()
    return {'ok': True}


# ── Subtasks ─────────────────────────────────────────────────────────────────

def _subtask_qs():
    return Task.objects.select_related('assignee', 'parent_task', 'project')


@router.get('/{task_id}/subtasks', response=List[SubTaskOut], summary='서브태스크 목록')
def list_subtasks(request: HttpRequest, task_id: UUID):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)
    return _subtask_qs().filter(parent_task_id=task_id).order_by('sub_number')


@router.post('/{task_id}/subtasks', response=SubTaskOut, summary='서브태스크 생성')
def create_subtask(request: HttpRequest, task_id: UUID, payload: SubTaskCreate):
    parent = get_object_or_404(Task.objects.select_related('project'), pk=task_id)
    _get_project(parent.project_id, request.auth)

    if parent.parent_task_id is not None:
        raise HttpError(400, 'Subtasks cannot have subtasks')

    with transaction.atomic():
        max_sub = (
            Task.objects
            .filter(parent_task=parent)
            .order_by('-sub_number')
            .values_list('sub_number', flat=True)
            .first()
        ) or 0

        subtask = Task.objects.create(
            project=parent.project,
            parent_task=parent,
            created_by=request.auth,
            title=payload.title,
            assignee_id=payload.assignee_id,
            status='todo',
            priority='none',
            sub_number=max_sub + 1,
            number=0,
            sort_order=max_sub + 1,
        )
    return _subtask_qs().get(pk=subtask.pk)


@router.patch('/{task_id}/subtasks/{subtask_id}', response=SubTaskOut, summary='서브태스크 수정')
def update_subtask(request: HttpRequest, task_id: UUID, subtask_id: UUID, payload: SubTaskUpdate):
    subtask = get_object_or_404(_subtask_qs(), pk=subtask_id, parent_task_id=task_id)
    _get_project(subtask.project_id, request.auth)

    data = payload.dict(exclude_unset=True)
    if 'is_done' in data:
        subtask.status = 'done' if data.pop('is_done') else 'todo'
    if 'assignee_id' in data:
        subtask.assignee_id = data.pop('assignee_id')
    for k, v in data.items():
        setattr(subtask, k, v)
    subtask.save()
    return _subtask_qs().get(pk=subtask.pk)


@router.delete('/{task_id}/subtasks/{subtask_id}', summary='서브태스크 삭제')
def delete_subtask(request: HttpRequest, task_id: UUID, subtask_id: UUID):
    subtask = get_object_or_404(Task, pk=subtask_id, parent_task_id=task_id)
    _get_project(subtask.project_id, request.auth)
    subtask.delete()
    return {'ok': True}


# ── Dependencies ─────────────────────────────────────────────────────────────

def _dep_qs():
    return Task.objects.select_related('project', 'assignee', 'created_by')


def _has_cycle(blocked_id: UUID, blocking_id: UUID) -> bool:
    """blocking_task의 의존 체인에 blocked_task가 있으면 순환 의존."""
    visited = set()
    queue = [blocking_id]
    while queue:
        current = queue.pop()
        if current in visited:
            continue
        visited.add(current)
        if current == blocked_id:
            return True
        for dep in TaskDependency.objects.filter(blocked_task_id=current).values_list('blocking_task_id', flat=True):
            queue.append(dep)
    return False


@router.get('/{task_id}/dependencies', response=DependenciesOut, summary='의존 이슈 목록')
def list_dependencies(request: HttpRequest, task_id: UUID):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)
    blocking = _dep_qs().filter(blocking_dependencies__blocked_task_id=task_id)
    blocked = _dep_qs().filter(dependencies__blocking_task_id=task_id)
    return {'blocking': list(blocking), 'blocked': list(blocked)}


@router.post('/{task_id}/dependencies', response=DependenciesOut, summary='의존 이슈 추가')
def add_dependency(request: HttpRequest, task_id: UUID, payload: DependencyAddIn):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)

    blocking_task = get_object_or_404(Task, pk=payload.blocking_task_id)
    _get_project(blocking_task.project_id, request.auth)

    if task_id == payload.blocking_task_id:
        raise HttpError(400, 'Cannot depend on itself')
    if _has_cycle(task_id, payload.blocking_task_id):
        raise HttpError(400, 'Circular dependency detected')

    TaskDependency.objects.get_or_create(
        blocked_task=task, blocking_task=blocking_task,
        defaults={'created_by': request.auth},
    )
    return list_dependencies(request, task_id)


@router.delete('/{task_id}/dependencies/{blocking_task_id}', summary='의존 이슈 제거')
def remove_dependency(request: HttpRequest, task_id: UUID, blocking_task_id: UUID):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)
    dep = get_object_or_404(TaskDependency, blocked_task_id=task_id, blocking_task_id=blocking_task_id)
    dep.delete()
    return {'ok': True}


# ── Comments ─────────────────────────────────────────────────────────────────

@router.get('/{task_id}/comments', response=List[CommentOut], summary='댓글 목록')
def list_comments(request: HttpRequest, task_id: UUID):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)
    return task.comments.select_related('user').order_by('created_at')


@router.post('/{task_id}/comments', response=CommentOut, summary='댓글 작성')
def create_comment(request: HttpRequest, task_id: UUID, payload: CommentCreate):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)

    comment = TaskComment.objects.create(
        task=task,
        user=request.auth,
        content=payload.content,
    )
    TaskActivity.objects.create(task=task, user=request.auth, activity_type='commented', data={})

    # Parse @mentions and create notifications
    mention_names = re.findall(r'@(\S+)', payload.content)
    if mention_names:
        from projects.models import ProjectMember
        members = ProjectMember.objects.filter(
            project=task.project
        ).select_related('user')
        for m in members:
            display = m.user.display_name if hasattr(m.user, 'display_name') else (m.user.first_name or m.user.email)
            # Match against first_name or display_name
            for name in mention_names:
                if display.lower() == name.lower() or m.user.first_name.lower() == name.lower():
                    if m.user != request.auth:
                        Notification.objects.create(
                            recipient=m.user,
                            actor=request.auth,
                            type='mention',
                            task=task,
                            comment=comment,
                        )
                    break

    _dispatch(task.project_id, 'task.comment', {
        'task_id': str(task.id),
        'task_ref': f'{task.project.key}-{task.number}',
        'task_title': task.title,
        'comment_id': str(comment.id),
        'author': request.auth.display_name,
    })
    return comment


@router.delete('/{task_id}/comments/{comment_id}', summary='댓글 삭제')
def delete_comment(request: HttpRequest, task_id: UUID, comment_id: UUID):
    task = get_object_or_404(Task, pk=task_id)
    _get_project(task.project_id, request.auth)
    comment = get_object_or_404(TaskComment, pk=comment_id, task=task, user=request.auth)
    comment.delete()
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

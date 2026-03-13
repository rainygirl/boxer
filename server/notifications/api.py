from typing import List, Optional
from uuid import UUID
from ninja import Router, Schema
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from datetime import datetime
from accounts.schemas import UserOut
from tasks.models import Notification

router = Router()


class NotificationOut(Schema):
    id: UUID
    type: str
    read: bool
    created_at: datetime
    actor: Optional[UserOut] = None
    task_id: Optional[UUID] = None
    task_ref: Optional[str] = None
    task_title: Optional[str] = None
    project_id: Optional[UUID] = None

    @staticmethod
    def resolve_task_id(obj) -> Optional[UUID]:
        return obj.task_id

    @staticmethod
    def resolve_task_ref(obj) -> Optional[str]:
        if obj.task:
            return f"{obj.task.project.key}-{obj.task.number}"
        return None

    @staticmethod
    def resolve_task_title(obj) -> Optional[str]:
        return obj.task.title if obj.task else None

    @staticmethod
    def resolve_project_id(obj) -> Optional[UUID]:
        return obj.task.project_id if obj.task else None


@router.get('/', response=List[NotificationOut], summary='알림 목록')
def list_notifications(request: HttpRequest):
    return (
        Notification.objects
        .filter(recipient=request.auth)
        .select_related('actor', 'task', 'task__project')
        .order_by('read', '-created_at')[:30]
    )


@router.patch('/{notification_id}/read', response=NotificationOut, summary='알림 읽음 처리')
def mark_read(request: HttpRequest, notification_id: UUID):
    notif = get_object_or_404(Notification, pk=notification_id, recipient=request.auth)
    notif.read = True
    notif.save(update_fields=['read'])
    notif.refresh_from_db()
    return notif


@router.post('/read-all', summary='모든 알림 읽음 처리')
def mark_all_read(request: HttpRequest):
    Notification.objects.filter(recipient=request.auth, read=False).update(read=True)
    return {'ok': True}

from ninja import Schema
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID
from accounts.schemas import UserOut

TaskStatus = Literal['backlog', 'todo', 'in_progress', 'done', 'confirmed', 'cancelled']
TaskPriority = Literal['urgent', 'high', 'medium', 'low', 'none']


class TaskCreate(Schema):
    title: str
    description: str = ''
    status: TaskStatus = 'backlog'
    priority: TaskPriority = 'medium'
    assignee_id: Optional[int] = None


class TaskUpdate(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[int] = None


class TaskMove(Schema):
    status: TaskStatus
    sort_order: float


class AttachmentOut(Schema):
    id: UUID
    filename: str
    content_type: str
    size: int
    url: str
    uploaded_by: UserOut
    created_at: datetime


class TaskOut(Schema):
    id: UUID
    project_id: UUID
    title: str
    description: str
    status: str
    priority: str
    assignee: Optional[UserOut] = None
    sort_order: float
    created_by: UserOut
    created_at: datetime
    updated_at: datetime

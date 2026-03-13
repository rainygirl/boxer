from ninja import Schema
from typing import Optional, Literal
from datetime import datetime, date as date_type
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
    due_date: Optional[date_type] = None


class TaskUpdate(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[int] = None
    due_date: Optional[date_type] = None


class TaskMove(Schema):
    status: TaskStatus
    sort_order: float
    project_id: Optional[UUID] = None


class TaskActivityOut(Schema):
    id: UUID
    activity_type: str
    data: dict
    user: Optional[UserOut] = None
    created_at: datetime


class AttachmentOut(Schema):
    id: UUID
    filename: str
    content_type: str
    size: int
    url: str
    uploaded_by: UserOut
    created_at: datetime


class DependencyTaskOut(Schema):
    """의존 관계에서 참조되는 이슈의 요약 정보"""
    id: UUID
    ref: str
    title: str
    status: str
    priority: str
    project_id: UUID

    @staticmethod
    def resolve_ref(obj) -> str:
        return f"{obj.project.key}-{obj.number}"


class DependencyAddIn(Schema):
    blocking_task_id: UUID


class DependenciesOut(Schema):
    blocking: list[DependencyTaskOut]  # 이 이슈가 기다리는 이슈들
    blocked: list[DependencyTaskOut]   # 이 이슈를 기다리는 이슈들


class SubTaskCreate(Schema):
    title: str
    assignee_id: Optional[int] = None


class SubTaskUpdate(Schema):
    title: Optional[str] = None
    assignee_id: Optional[int] = None
    is_done: Optional[bool] = None


class SubTaskOut(Schema):
    id: UUID
    parent_task_id: UUID
    title: str
    status: str
    assignee: Optional[UserOut] = None
    sub_number: int
    ref: str

    @staticmethod
    def resolve_ref(obj) -> str:
        return f"{obj.project.key}-{obj.parent_task.number}-{obj.sub_number}"


class TaskOut(Schema):
    id: UUID
    project_id: UUID
    title: str
    description: str
    status: str
    priority: str
    assignee: Optional[UserOut] = None
    number: int
    ref: str
    sort_order: float
    due_date: Optional[date_type] = None
    created_by: UserOut
    created_at: datetime
    updated_at: datetime
    subtasks: list[SubTaskOut] = []

    @staticmethod
    def resolve_ref(obj) -> str:
        return f"{obj.project.key}-{obj.number}"

    @staticmethod
    def resolve_subtasks(obj) -> list:
        return list(obj.subtasks.all())


class CommentCreate(Schema):
    content: str


class CommentOut(Schema):
    id: UUID
    task_id: UUID
    user: Optional[UserOut] = None
    content: str
    created_at: datetime
    updated_at: datetime


class TaskSearchResult(Schema):
    id: UUID
    project_id: UUID
    project_color: str
    ref: str
    title: str
    status: str

    @staticmethod
    def resolve_project_color(obj) -> str:
        return obj.project.color

    @staticmethod
    def resolve_ref(obj) -> str:
        return f"{obj.project.key}-{obj.number}"

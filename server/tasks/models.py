import uuid
from django.db import models
from django.conf import settings


class Task(models.Model):
    STATUS_CHOICES = [
        ('backlog', 'Backlog'),
        ('todo', 'Todo'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('urgent', 'Urgent'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('none', 'None'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='backlog')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
    )
    number = models.PositiveIntegerField(default=0)  # sequential per project, assigned on create
    sub_number = models.PositiveIntegerField(default=0)  # sequential per parent task (subtasks only)
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks',
    )
    sort_order = models.FloatField(default=0)
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tasks'
        ordering = ['sort_order', 'created_at']
        indexes = [
            models.Index(fields=['project', 'status', 'sort_order']),
        ]

    def __str__(self):
        return self.title


class TaskActivity(models.Model):
    ACTIVITY_TYPES = [
        ('created', 'Created'),
        ('status_changed', 'Status Changed'),
        ('priority_changed', 'Priority Changed'),
        ('assignee_changed', 'Assignee Changed'),
        ('content_edited', 'Content Edited'),
        ('due_date_changed', 'Due Date Changed'),
        ('project_moved', 'Project Moved'),
        ('commented', 'Commented'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='task_activities',
    )
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_activities'
        ordering = ['-created_at']


class TaskDependency(models.Model):
    """blocked_task는 blocking_task가 완료되어야 진행할 수 있다."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blocked_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependencies')
    blocking_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='blocking_dependencies')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_dependencies'
        unique_together = ('blocked_task', 'blocking_task')


class TaskComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task_comments'
        ordering = ['created_at']


class Notification(models.Model):
    TYPES = [('mention', 'Mention'), ('assigned', 'Assigned')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sent_notifications')
    type = models.CharField(max_length=20, choices=TYPES)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(TaskComment, on_delete=models.CASCADE, null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']


class TaskAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file_key = models.CharField(max_length=500)
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100, default='application/octet-stream')
    size = models.PositiveIntegerField()
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_attachments',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_attachments'
        ordering = ['created_at']

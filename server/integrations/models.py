import uuid
from django.db import models
from django.conf import settings


class GitHubIntegration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.OneToOneField(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='github_integration',
    )
    repo_owner = models.CharField(max_length=255, blank=True, default='')
    repo_name = models.CharField(max_length=255, blank=True, default='')
    webhook_secret = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'github_integrations'

    @property
    def is_configured(self):
        return bool(self.repo_owner and self.repo_name)


class ProjectWebhook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='webhooks',
    )
    url = models.URLField(max_length=500)
    secret = models.CharField(max_length=255, blank=True, default='')
    # Empty list = subscribe to all events
    events = models.JSONField(default=list, blank=True)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_webhooks'
        ordering = ['created_at']

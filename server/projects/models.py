import uuid
from django.db import models
from django.conf import settings


def _index_to_key(n: int) -> str:
    """
    n=0 → AA, n=675 → ZZ, n=676 → AAA, ...
    Starts at 2-char, expands when exhausted.
    """
    length = 2
    total = 0
    while True:
        count = 26 ** length
        if n < total + count:
            break
        total += count
        length += 1

    rem = n - total
    result = ''
    for _ in range(length):
        result = chr(ord('A') + rem % 26) + result
        rem //= 26
    return result


def generate_project_key() -> str:
    """Return the next auto-generated key not already in use."""
    existing = set(Project.objects.values_list('key', flat=True))
    i = 0
    while True:
        candidate = _index_to_key(i)
        if candidate not in existing:
            return candidate
        i += 1


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    color = models.CharField(max_length=7, default='#6366f1')
    disabled_statuses = models.JSONField(default=list, blank=True)
    key = models.CharField(max_length=20, unique=True, blank=True)
    next_task_number = models.PositiveIntegerField(default=1)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMember',
        related_name='projects',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = generate_project_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProjectMember(models.Model):
    ROLE_CHOICES = [('owner', 'Owner'), ('member', 'Member'), ('viewer', 'Viewer')]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_members'
        unique_together = ('project', 'user')


class ProjectFavorite(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_projects')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_favorites'
        unique_together = ('project', 'user')

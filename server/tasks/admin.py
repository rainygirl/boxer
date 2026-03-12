from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'priority', 'assignee', 'created_at')
    list_filter = ('status', 'priority', 'project')
    search_fields = ('title', 'description')

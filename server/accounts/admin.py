from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'display_name', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra', {'fields': ('avatar_url',)}),
    )

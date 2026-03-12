from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar_url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email or self.username

    @property
    def display_name(self):
        return self.get_full_name() or self.username or self.email

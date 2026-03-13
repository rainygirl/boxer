from django.contrib import admin
from django.urls import path, include
from .api import api
from accounts.views import jwt_redirect_view
from integrations.github_webhook import github_webhook_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('auth/jwt/', jwt_redirect_view, name='jwt_redirect'),
    path('api/', api.urls),
    path('webhook/github/<uuid:project_id>/', github_webhook_view, name='github_webhook'),
]

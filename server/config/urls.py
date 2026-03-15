from django.contrib import admin
from django.urls import path, include, re_path
from django.http import FileResponse, HttpResponseNotFound
from django.conf import settings as django_settings
from .api import api
from accounts.views import jwt_redirect_view
from integrations.github_webhook import github_webhook_view


def spa_fallback(request, path=''):
    index = django_settings.FRONTEND_BUILD_DIR / 'index.html'
    if index.exists():
        return FileResponse(open(index, 'rb'), content_type='text/html')
    return HttpResponseNotFound('Frontend not built. Run: npm run build')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('auth/jwt/', jwt_redirect_view, name='jwt_redirect'),
    path('api/', api.urls),
    path('webhook/github/<uuid:project_id>/', github_webhook_view, name='github_webhook'),
    re_path(r'^.*$', spa_fallback),  # SPA fallback — must be last
]

from django.contrib import admin
from django.urls import path, include
from .api import api
from accounts.views import jwt_redirect_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('auth/jwt/', jwt_redirect_view, name='jwt_redirect'),
    path('api/', api.urls),
]

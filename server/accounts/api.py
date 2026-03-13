from datetime import datetime, timedelta, timezone

import jwt
import requests as http_requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError

from .schemas import UserOut

router = Router()
User = get_user_model()


class ProfileUpdate(Schema):
    name: str
    job_title: str = ''


class GoogleCallbackIn(Schema):
    code: str
    redirect_uri: str


class TokenOut(Schema):
    token: str


class GoogleConfigOut(Schema):
    client_id: str


@router.get('/google-config', auth=None, response=GoogleConfigOut, summary='Google OAuth 설정')
def google_config(request: HttpRequest):
    return {'client_id': settings.SOCIALACCOUNT_PROVIDERS.get('google', {}).get('APP', {}).get('client_id', '')}


@router.post('/google', auth=None, response=TokenOut, summary='Google OAuth 코드 교환')
def google_login(request: HttpRequest, payload: GoogleCallbackIn):
    # 1) Exchange authorization code for tokens
    token_resp = http_requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': payload.code,
            'client_id': settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'],
            'client_secret': settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret'],
            'redirect_uri': payload.redirect_uri,
            'grant_type': 'authorization_code',
        },
        timeout=10,
    )
    token_data = token_resp.json()
    if 'error' in token_data:
        raise HttpError(400, token_data.get('error_description', 'OAuth error'))

    # 2) Fetch user info
    userinfo_resp = http_requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {token_data["access_token"]}'},
        timeout=10,
    )
    userinfo = userinfo_resp.json()
    email = userinfo.get('email', '')
    if not email:
        raise HttpError(400, 'No email returned from Google')

    # 3) Get or create user — look up by email first to find existing allauth accounts
    is_new_user = False
    user = User.objects.filter(email=email).order_by('id').first()
    if not user:
        # Generate a safe username from the email local part
        base = email.split('@')[0]
        username = base
        n = 1
        while User.objects.filter(username=username).exists():
            username = f'{base}{n}'
            n += 1
        user = User.objects.create_user(username=username, email=email)
        is_new_user = True

    # Set display name from Google if not customised
    google_name = userinfo.get('name', '')
    if google_name and not user.first_name:
        user.first_name = google_name

    # 4) Upload avatar to R2 (or fall back to Google URL)
    picture = userinfo.get('picture', '')
    if picture:
        already_in_r2 = (
            user.avatar_url
            and not user.avatar_url.startswith('https://lh')
        )
        if not already_in_r2:
            from tasks.r2 import upload_avatar
            r2_url = upload_avatar(user.pk, picture)
            user.avatar_url = r2_url or picture

    user.save(update_fields=['email', 'first_name', 'avatar_url'])

    # Auto-join public projects for new users
    if is_new_user:
        from projects.models import Project, ProjectMember
        for proj in Project.objects.filter(visibility='public'):
            ProjectMember.objects.get_or_create(project=proj, user=user, defaults={'role': 'member'})

    # 5) Issue JWT
    token = jwt.encode(
        {
            'sub': str(user.pk),
            'email': user.email,
            'name': user.display_name,
            'exp': datetime.now(tz=timezone.utc) + timedelta(days=7),
        },
        settings.JWT_SECRET,
        algorithm='HS256',
    )
    return {'token': token}


@router.get('/me', response=UserOut, summary='현재 사용자 정보')
def me(request: HttpRequest):
    return request.auth


@router.patch('/me', response=UserOut, summary='프로필 수정')
def update_me(request: HttpRequest, payload: ProfileUpdate):
    user = request.auth
    user.first_name = payload.name.strip()
    user.last_name = ''
    user.job_title = payload.job_title.strip()
    user.save(update_fields=['first_name', 'last_name', 'job_title'])
    return user

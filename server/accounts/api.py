from ninja import Router
from ninja import Schema
from django.http import HttpRequest
from .schemas import UserOut

router = Router()


class ProfileUpdate(Schema):
    name: str


@router.get('/me', response=UserOut, summary='현재 사용자 정보')
def me(request: HttpRequest):
    return request.auth


@router.patch('/me', response=UserOut, summary='프로필 수정')
def update_me(request: HttpRequest, payload: ProfileUpdate):
    user = request.auth
    user.first_name = payload.name.strip()
    user.last_name = ''
    user.save(update_fields=['first_name', 'last_name'])
    return user

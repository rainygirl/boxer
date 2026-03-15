from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class BoxerSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_auto_signup_allowed(self, request, sociallogin):
        return True

    def pre_social_login(self, request, sociallogin):
        """기존 이메일 계정이 있으면 소셜 계정을 자동 연결"""
        if sociallogin.is_existing:
            return
        email = sociallogin.user.email
        if not email:
            return
        try:
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

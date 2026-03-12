from datetime import datetime, timedelta, timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.conf import settings
import jwt


@login_required
def jwt_redirect_view(request):
    user = request.user

    # Update avatar from social account if available
    try:
        social = user.socialaccount_set.filter(provider='google').first()
        if social:
            picture = social.extra_data.get('picture', '')
            if picture and not user.avatar_url:
                user.avatar_url = picture
                user.save(update_fields=['avatar_url'])
    except Exception:
        pass

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

    # Invalidate session — we use JWT from here on
    from django.contrib.auth import logout
    logout(request)

    return redirect(f"{settings.CLIENT_URL}/auth/callback?token={token}")

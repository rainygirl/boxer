import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Google OAuth SocialApp 및 Site 초기 설정'

    def handle(self, *args, **kwargs):
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
        secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')

        # Site 설정 — dev에서 allauth가 redirect_uri를 5173(Vite proxy)으로 만들도록
        site, _ = Site.objects.get_or_create(id=1)
        if site.domain in ('example.com', 'localhost:4000'):
            site.domain = 'localhost:5173'
            site.name = 'Boxer Dev'
            site.save()

        if not client_id or not secret:
            self.stdout.write(self.style.WARNING('GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET 미설정 — 건너뜁니다.'))
            return

        from allauth.socialaccount.models import SocialApp
        app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={'name': 'Google', 'client_id': client_id, 'secret': secret},
        )
        if not created:
            app.client_id = client_id
            app.secret = secret
            app.save()
        if site not in app.sites.all():
            app.sites.add(site)

        verb = 'created' if created else 'updated'
        self.stdout.write(self.style.SUCCESS(f'Google SocialApp {verb}'))

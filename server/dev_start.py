#!/usr/bin/env python3
"""
개발 서버 시작 전 필요한 환경변수를 체크하고,
미설정된 항목이 있으면 설정 URL을 브라우저에서 엽니다.
"""
import os
import sys
import webbrowser
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR.parent / '.env')  # 프로젝트 루트 .env

CHECKS = [
    {
        'name': 'Google OAuth',
        'keys': ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'],
        'url': 'https://console.cloud.google.com/apis/credentials',
        'hint': 'Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 만드세요.',
        'optional': False,
    },
    {
        'name': 'Cloudflare R2 (첨부파일)',
        'keys': ['R2_ACCOUNT_ID', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY'],
        'url': 'https://dash.cloudflare.com/?to=/:account/r2/overview',
        'hint': '없으면 파일 첨부 기능이 비활성화됩니다. 버킷 생성 후 API 토큰을 발급받으세요.',
        'optional': True,
    },
]

missing_required = False

for check in CHECKS:
    missing = [k for k in check['keys'] if not os.environ.get(k)]
    if not missing:
        continue

    optional = check.get('optional', False)
    tag = '⚠️  [선택]' if optional else '❌ [필수]'
    print(f"\n{tag} {check['name']} 환경변수 누락: {', '.join(missing)}")
    print(f"       {check['hint']}")
    print(f"       브라우저 열기 → {check['url']}")
    webbrowser.open(check['url'])

    if not optional:
        missing_required = True

if missing_required:
    print()
    print("필수 환경변수가 없어 서버를 시작하지 않습니다.")
    print("server/.env 파일을 채운 뒤 다시 실행하세요.")
    print()
    sys.exit(1)

print("\n✅ 환경변수 확인 완료 — 서버를 시작합니다.\n")

# Replace this process with the Django dev server
os.execvp(sys.executable, [sys.executable, 'manage.py', 'runserver', '4173'])

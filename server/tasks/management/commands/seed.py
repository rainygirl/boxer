"""
Seed command — creates a convincing demo dataset.

Usage:
    python3 manage.py seed
    python3 manage.py seed --reset   # drops and re-migrates first
"""

import random
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from projects.models import Project, ProjectMember, ProjectFavorite
from tasks.models import Task, TaskActivity, TaskComment, TaskDependency, Notification

User = get_user_model()

# ── helpers ──────────────────────────────────────────────────────────────────

def rand_date(days_back=60, days_forward=30):
    offset = random.randint(-days_back, days_forward)
    return date.today() + timedelta(days=offset)

def past_dt(days_back=30):
    return timezone.now() - timedelta(days=random.uniform(0, days_back))

# ── data ─────────────────────────────────────────────────────────────────────

USERS = [
    dict(username='alice',   first_name='Alice',   last_name='Park',    email='alice@coroke.net',   avatar_url='https://api.dicebear.com/7.x/avataaars/svg?seed=alice',  job_title='Product Manager'),
    dict(username='brian',   first_name='Brian',   last_name='Kim',     email='brian@coroke.net',   avatar_url='https://api.dicebear.com/7.x/avataaars/svg?seed=brian',  job_title='Backend Engineer'),
    dict(username='chloe',   first_name='Chloe',   last_name='Lee',     email='chloe@coroke.net',   avatar_url='https://api.dicebear.com/7.x/avataaars/svg?seed=chloe',  job_title='Frontend Engineer'),
    dict(username='daniel',  first_name='Daniel',  last_name='Choi',    email='daniel@coroke.net',  avatar_url='https://api.dicebear.com/7.x/avataaars/svg?seed=daniel', job_title='Mobile Developer'),
    dict(username='emma',    first_name='Emma',    last_name='Yoon',    email='emma@coroke.net',    avatar_url='https://api.dicebear.com/7.x/avataaars/svg?seed=emma',   job_title='UX Designer'),
]

PROJECTS = [
    dict(
        name='Boxer',
        key='BOX',
        color='#6366f1',
        description='Boxer 자체 개발 프로젝트. 칸반 보드, 알림, GitHub 연동 등 핵심 기능을 관리합니다.',
        owner_idx=0,
        member_idxs=[1, 2, 3, 4],
        visibility='public',
    ),
    dict(
        name='Marketing Site',
        key='MKT',
        color='#10b981',
        description='랜딩 페이지 및 마케팅 웹사이트 리뉴얼 프로젝트.',
        owner_idx=2,
        member_idxs=[0, 1, 4],
        visibility='public',
    ),
    dict(
        name='Mobile App',
        key='MOB',
        color='#f59e0b',
        description='iOS / Android 네이티브 앱 개발. React Native 기반.',
        owner_idx=1,
        member_idxs=[0, 2, 3],
        visibility='public',
    ),
]

# (title, status, priority, assignee_idx, due_offset, description)
BOX_TASKS = [
    # in_progress
    ('GitHub 연동 — PR 자동 닫기 구현', 'in_progress', 'urgent', 0, 3,
     'PR merge 시 `fixes BOX-N` 키워드를 파싱해 태스크를 자동으로 done 처리합니다.'),
    ('아웃고잉 Webhook 발송 기능', 'in_progress', 'high', 1, 5,
     'task.created / task.updated / task.comment 이벤트를 외부 URL로 POST 발송. HMAC-SHA256 서명 포함.'),
    ('알림 UI 개선 — 이름 직접 표시', 'in_progress', 'medium', 2, 7,
     '\"회원님\" 고정 문구 대신 실제 수신자 이름을 표시. 한글 조사(을/를) 자동 처리.'),
    # todo
    ('다크모드 블랙 테마 폴리싱', 'todo', 'medium', 3, 10,
     '블랙 테마에서 border, shadow 색상 일부가 라이트 테마 색을 참조하는 버그 수정.'),
    ('파일 첨부 — 이미지 미리보기', 'todo', 'low', 4, 14,
     'R2에 업로드된 이미지를 태스크 상세에서 인라인 미리보기로 표시.'),
    ('모바일 칸반 스와이프 제스처', 'todo', 'medium', 1, 18,
     '모바일에서 칸반 컬럼을 수평 스와이프로 전환할 수 있도록 UX 개선.'),
    ('프로젝트 보고서 — CSV 내보내기', 'todo', 'low', 2, 21,
     '상태 분포, 사이클타임 데이터를 CSV로 다운로드하는 버튼 추가.'),
    # backlog
    ('Slack 알림 Webhook 템플릿', 'backlog', 'medium', None, 30,
     'Slack incoming webhook 포맷에 맞는 페이로드 템플릿을 아웃고잉 Webhook 설정에 추가.'),
    ('태스크 일괄 상태 변경', 'backlog', 'low', None, 35,
     '칸반 뷰에서 여러 태스크를 체크박스로 선택 후 상태/담당자를 일괄 변경.'),
    ('2FA 로그인 지원', 'backlog', 'medium', None, 45,
     'Google OAuth 외 TOTP 기반 2FA 옵션 추가.'),
    # done
    ('SvelteKit 서버 라우트로 GitHub Webhook 프록시', 'done', 'high', 0, -5,
     '`/webhook/github/[project_id]/` 라우트에서 Django로 프록시. CNAME 서브도메인 불필요.'),
    ('헤더 높이 60px 통일', 'done', 'low', 2, -8,
     '사이드바, 프로젝트 헤더, 각 페이지 헤더의 세로 높이를 모두 60px로 고정.'),
    ('프로젝트 설정 모달 탭 구조로 전환', 'done', 'medium', 1, -12,
     'General / GitHub / Webhooks 탭으로 분리. 삭제 기능은 General 탭 하단 링크로 이동.'),
    ('멤버 초대 모달 컴포넌트화', 'done', 'medium', 3, -15,
     'InviteMemberModal을 공용 컴포넌트로 분리. 사이드바와 /app/members 양쪽에서 재사용.'),
    # confirmed
    ('README.md 오픈소스 공개용 정비', 'confirmed', 'medium', 0, -3,
     '.env 보안 주의사항, 설치 가이드, Tech Stack, 주요 기능 섹션 포함.'),
    # cancelled
    ('Cmd+K 전역 검색 단축키', 'cancelled', 'low', None, -20,
     '전역 키다운 핸들러 충돌 및 입력 필드 방해 문제로 기능 제거 결정.'),
]

MKT_TASKS = [
    ('랜딩 페이지 히어로 섹션 리디자인', 'in_progress', 'urgent', 2, 4,
     '신규 브랜드 가이드라인에 맞춰 히어로 섹션 비주얼 전면 교체.'),
    ('SEO 메타태그 및 OG 이미지 설정', 'in_progress', 'high', 0, 6,
     '각 페이지별 title, description, og:image를 설정. og:image는 1200×630 PNG.'),
    ('고객 후기 섹션 추가', 'todo', 'medium', 4, 10,
     '실제 사용자 3인의 인터뷰 발췌를 카드 형태로 배치.'),
    ('구글 애널리틱스 4 연동', 'todo', 'low', 1, 15,
     'GA4 태그를 SvelteKit 레이아웃에 삽입. 페이지뷰 및 CTA 클릭 이벤트 트래킹.'),
    ('뉴스레터 구독 폼 제작', 'backlog', 'medium', None, 25,
     'Mailchimp API 연동. 이메일 입력 → 구독 완료 토스트 표시.'),
    ('다국어 랜딩 페이지 (영어 버전)', 'backlog', 'low', None, 40,
     '한국어 기본 페이지를 영어로 현지화. hreflang 태그 추가.'),
    ('성능 최적화 — LCP 2.5s 이하', 'done', 'high', 2, -7,
     'Next.js Image 컴포넌트 적용, 웹폰트 preload, CLS 0.1 이하 달성.'),
    ('Figma 디자인 시스템 컴포넌트 정의', 'confirmed', 'medium', 2, -10,
     '버튼, 인풋, 카드, 색상 토큰 등 공통 컴포넌트 Figma에 정의 완료.'),
]

MOB_TASKS = [
    ('로그인 화면 — Google OAuth 연동', 'done', 'urgent', 1, -14,
     'expo-auth-session으로 Google OAuth 구현. JWT를 SecureStore에 저장.'),
    ('칸반 뷰 모바일 렌더링', 'in_progress', 'high', 3, 5,
     'React Native에서 FlatList 기반 칸반 컬럼 렌더링. 수평 스크롤 지원.'),
    ('푸시 알림 — FCM 연동', 'in_progress', 'high', 0, 8,
     'Firebase Cloud Messaging 설정. 태스크 할당/멘션 시 푸시 발송.'),
    ('태스크 상세 화면', 'todo', 'medium', 2, 12,
     '제목, 설명, 상태, 담당자, 댓글을 표시하는 상세 화면 구현.'),
    ('오프라인 모드 — 로컬 캐시', 'backlog', 'low', None, 35,
     'AsyncStorage에 프로젝트/태스크 캐시. 오프라인 시 읽기 전용으로 동작.'),
    ('앱 아이콘 및 스플래시 스크린', 'todo', 'low', 3, 20,
     '1024×1024 앱 아이콘과 스플래시 스크린 에셋 적용.'),
    ('TestFlight / Play Console 내부 배포', 'backlog', 'medium', None, 45,
     '첫 번째 내부 테스트 빌드를 TestFlight과 Play Console 내부 트랙에 배포.'),
]

COMMENTS = {
    'BOX': [
        (0, [
            (0, 'HMAC 검증 로직은 `hmac.compare_digest`로 처리하면 타이밍 공격 방어도 됩니다.'),
            (1, '맞아요. 그리고 push 이벤트는 commits 배열을 순회해야 하고, PR은 closed+merged 조합만 처리해야 해요.'),
            (0, '확인했습니다. 지금 구현 중이에요.'),
        ]),
        (10, [
            (2, 'SvelteKit `+server.ts`는 `ssr=false`여도 동작하네요. 프록시 방식 괜찮은 것 같아요.'),
            (0, '맞아요. 페이지는 SSR 안 하지만 서버 라우트는 별개예요.'),
        ]),
        (11, [
            (3, '헤더 높이 DevTools로 재봤는데 사이드바가 61px나와서 `h-[60px] flex items-center`로 바꿨어요.'),
            (2, 'py-4에 텍스트 크기 더하면 딱 안 맞아서요. 고정값이 맞습니다.'),
        ]),
    ],
    'MKT': [
        (0, [
            (2, '히어로 섹션 시안 Figma에 올려놨어요. 피드백 주세요.'),
            (4, '전체적으로 좋은데 CTA 버튼 색상을 브랜드 컬러로 맞추면 좋겠어요.'),
            (2, '반영할게요!'),
        ]),
        (6, [
            (0, 'Lighthouse 점수 95 나왔어요. LCP 1.8s로 목표 달성했습니다.'),
            (2, '잘 됐네요. PR 리뷰해드릴게요.'),
        ]),
    ],
    'MOB': [
        (0, [
            (1, 'SecureStore 사용할 때 기기에 passcode 설정 안 되어 있으면 fallback이 필요해요.'),
            (3, '좋은 지적이에요. WHEN_UNLOCKED_THIS_DEVICE_ONLY 옵션으로 처리하면 됩니다.'),
        ]),
        (1, [
            (3, '칸반 FlatList에서 드래그 이슈가 있어요. `react-native-draggable-flatlist` 써볼까요?'),
            (1, '써봤는데 성능 괜찮았어요. 이번 스프린트에 적용해봅시다.'),
        ]),
    ],
}

ACTIVITIES = [
    ('status_changed', {'from': 'backlog', 'to': 'in_progress'}),
    ('priority_changed', {'from': 'low', 'to': 'high'}),
    ('assignee_changed', {'from': None, 'to': 'alice'}),
    ('status_changed', {'from': 'todo', 'to': 'in_progress'}),
    ('status_changed', {'from': 'in_progress', 'to': 'done'}),
]


class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Drop and re-migrate before seeding')

    def handle(self, *args, **options):
        if options['reset']:
            self._reset()

        self.stdout.write('Seeding users...')
        users = self._create_users()

        self.stdout.write('Seeding projects & tasks...')
        box = self._create_project(PROJECTS[0], users, BOX_TASKS, COMMENTS.get('BOX', []))
        mkt = self._create_project(PROJECTS[1], users, MKT_TASKS, COMMENTS.get('MKT', []))
        mob = self._create_project(PROJECTS[2], users, MOB_TASKS, COMMENTS.get('MOB', []))

        self.stdout.write('Adding favorites...')
        ProjectFavorite.objects.get_or_create(project=box, user=users[0])
        ProjectFavorite.objects.get_or_create(project=mkt, user=users[2])
        ProjectFavorite.objects.get_or_create(project=mob, user=users[1])

        self.stdout.write('Adding task dependencies...')
        self._add_dependencies(box)

        self.stdout.write('Adding notifications...')
        self._add_notifications(users, [box, mkt, mob])

        self.stdout.write(self.style.SUCCESS('Done! Seed data created successfully.'))

    # ── reset ─────────────────────────────────────────────────────────────────

    def _reset(self):
        import os, subprocess
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'boxer.db')
        db_path = os.path.normpath(db_path)
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(f'Removed {db_path}')
        from django.core.management import call_command
        call_command('migrate', '--run-syncdb', verbosity=0)
        self.stdout.write('Migrations applied.')

    # ── users ─────────────────────────────────────────────────────────────────

    def _create_users(self):
        users = []
        for d in USERS:
            u, created = User.objects.get_or_create(
                username=d['username'],
                defaults={
                    'first_name': d['first_name'],
                    'last_name': d['last_name'],
                    'email': d['email'],
                    'avatar_url': d['avatar_url'],
                    'job_title': d.get('job_title', ''),
                    'is_active': True,
                }
            )
            if created:
                u.set_unusable_password()
            u.job_title = d.get('job_title', '')
            u.save(update_fields=['job_title'] if not created else None)
            users.append(u)
        return users

    # ── projects ──────────────────────────────────────────────────────────────

    def _create_project(self, spec, users, task_specs, comment_specs):
        owner = users[spec['owner_idx']]
        proj, _ = Project.objects.get_or_create(
            key=spec['key'],
            defaults={
                'name': spec['name'],
                'description': spec['description'],
                'color': spec['color'],
                'owner': owner,
                'next_task_number': len(task_specs) + 1,
            }
        )
        proj.visibility = spec.get('visibility', 'private')
        proj.save(update_fields=['visibility'])

        # owner membership
        ProjectMember.objects.get_or_create(project=proj, user=owner, defaults={'role': 'owner'})
        for idx in spec['member_idxs']:
            ProjectMember.objects.get_or_create(project=proj, user=users[idx], defaults={'role': 'member'})

        # tasks
        tasks = []
        for i, (title, status, priority, assignee_idx, due_offset, desc) in enumerate(task_specs):
            assignee = users[assignee_idx] if assignee_idx is not None else None
            due = date.today() + timedelta(days=due_offset)
            t, created = Task.objects.get_or_create(
                project=proj,
                number=i + 1,
                defaults={
                    'title': title,
                    'description': desc,
                    'status': status,
                    'priority': priority,
                    'assignee': assignee,
                    'due_date': due,
                    'sort_order': float(i),
                    'created_by': owner,
                    'sub_number': 0,
                }
            )
            if created:
                TaskActivity.objects.create(
                    task=t,
                    user=owner,
                    activity_type='created',
                    data={},
                )
                # random extra activities
                for act_type, act_data in random.sample(ACTIVITIES, k=random.randint(1, 3)):
                    TaskActivity.objects.create(
                        task=t,
                        user=random.choice(users[:3]),
                        activity_type=act_type,
                        data=act_data,
                    )
            tasks.append(t)

        # comments
        all_members = [owner] + [users[i] for i in spec['member_idxs']]
        for task_idx, thread in comment_specs:
            if task_idx >= len(tasks):
                continue
            task = tasks[task_idx]
            for user_idx, content in thread:
                user = all_members[user_idx % len(all_members)]
                TaskComment.objects.get_or_create(
                    task=task,
                    user=user,
                    content=content,
                )

        # subtasks — each in_progress task gets its own relevant subtasks
        subtask_map = {
            # BOX
            'GitHub 연동 — PR 자동 닫기 구현': [
                ('HMAC 서명 검증 로직 작성', 'done'),
                ('push 이벤트 커밋 메시지 파싱', 'done'),
                ('PR closed+merged 이벤트 처리', 'in_progress'),
                ('태스크 자동 done 처리 연동', 'todo'),
            ],
            '아웃고잉 Webhook 발송 기능': [
                ('ProjectWebhook 모델 설계', 'done'),
                ('비동기 발송 스레드 구현', 'in_progress'),
                ('HMAC-SHA256 서명 헤더 추가', 'todo'),
                ('재시도 로직 검토', 'backlog'),
            ],
            '알림 UI 개선 — 이름 직접 표시': [
                ('한글 조사 josa 유틸 작성', 'done'),
                ('번역 키 플레이스홀더 수정', 'done'),
                ('NotificationBell 연동', 'in_progress'),
                ('notifications 페이지 연동', 'todo'),
            ],
            # MKT
            '랜딩 페이지 히어로 섹션 리디자인': [
                ('Figma 시안 확정', 'done'),
                ('히어로 컴포넌트 마크업', 'done'),
                ('애니메이션 및 반응형 적용', 'in_progress'),
                ('크로스 브라우저 QA', 'backlog'),
            ],
            'SEO 메타태그 및 OG 이미지 설정': [
                ('페이지별 title/description 목록 작성', 'done'),
                ('OG 이미지 1200×630 제작', 'in_progress'),
                ('hreflang 태그 삽입', 'todo'),
                ('Google Search Console 등록', 'backlog'),
            ],
            # MOB
            '칸반 뷰 모바일 렌더링': [
                ('FlatList 컬럼 레이아웃 구성', 'done'),
                ('수평 스크롤 터치 제스처 적용', 'in_progress'),
                ('드래그 앤 드롭 라이브러리 연동', 'todo'),
                ('iOS / Android 디바이스 QA', 'backlog'),
            ],
            '푸시 알림 — FCM 연동': [
                ('Firebase 프로젝트 설정 및 인증서 발급', 'done'),
                ('expo-notifications 초기화', 'in_progress'),
                ('디바이스 토큰 서버 등록 API', 'todo'),
                ('알림 수신 핸들러 구현', 'backlog'),
            ],
        }

        in_prog = [t for t in tasks if t.status == 'in_progress']
        for parent in in_prog:
            subs = subtask_map.get(parent.title)
            if not subs:
                continue
            for sub_i, (sub_title, sub_status) in enumerate(subs):
                Task.objects.get_or_create(
                    project=proj,
                    parent_task=parent,
                    sub_number=sub_i + 1,
                    defaults={
                        'title': sub_title,
                        'status': sub_status,
                        'priority': 'medium',
                        'sort_order': float(sub_i),
                        'created_by': owner,
                        'number': 0,
                    }
                )

        proj.next_task_number = len(task_specs) + 1
        proj.save(update_fields=['next_task_number'])
        return proj

    # ── dependencies ─────────────────────────────────────────────────────────

    def _add_dependencies(self, proj):
        tasks = list(proj.tasks.filter(parent_task=None).order_by('number'))
        if len(tasks) < 4:
            return
        pairs = [(tasks[1], tasks[0]), (tasks[2], tasks[0]), (tasks[3], tasks[1])]
        for blocked, blocking in pairs:
            TaskDependency.objects.get_or_create(
                blocked_task=blocked,
                blocking_task=blocking,
                defaults={'created_by': proj.owner},
            )

    # ── notifications ─────────────────────────────────────────────────────────

    def _add_notifications(self, users, projects):
        for proj in projects:
            tasks = list(proj.tasks.filter(parent_task=None)[:5])
            for task in tasks:
                if task.assignee and task.assignee != proj.owner:
                    Notification.objects.get_or_create(
                        recipient=task.assignee,
                        actor=proj.owner,
                        type='assigned',
                        task=task,
                        defaults={'read': random.choice([True, False])},
                    )
        # mention notifications
        for proj in projects:
            tasks = list(proj.tasks.filter(parent_task=None)[:3])
            members = list(proj.memberships.select_related('user'))
            for task in tasks:
                if len(members) >= 2:
                    actor = random.choice(members).user
                    recipient = random.choice([m.user for m in members if m.user != actor])
                    Notification.objects.get_or_create(
                        recipient=recipient,
                        actor=actor,
                        type='mention',
                        task=task,
                        defaults={'read': random.choice([True, False])},
                    )

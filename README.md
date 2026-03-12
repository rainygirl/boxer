# Boxer

Linear 스타일의 팀 태스크 관리 도구.

- **백엔드**: Django 6 + Django Ninja + SQLite
- **프론트엔드**: SvelteKit + Svelte 5 + Tailwind CSS
- **인증**: Google OAuth 2.0 (django-allauth) → JWT
- **드래그앤드롭**: svelte-dnd-action

---

## 처음 시작하기

### 1. Google OAuth 앱 만들기

[Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials → **OAuth 2.0 Client ID 생성**

- Application type: `Web application`
- Authorized redirect URIs에 추가:
  ```
  http://localhost:4000/accounts/google/login/callback/
  ```
- 생성 후 **Client ID**와 **Client Secret** 복사

### 2. 서버 환경 변수 설정

```bash
cp server/.env.example server/.env
```

`server/.env`를 열고 아래 항목 채우기:

```env
SECRET_KEY=랜덤한-긴-문자열-직접-만들기
JWT_SECRET=다른-랜덤한-긴-문자열
GOOGLE_CLIENT_ID=구글에서-받은-클라이언트-id
GOOGLE_CLIENT_SECRET=구글에서-받은-클라이언트-시크릿
```

`SECRET_KEY` / `JWT_SECRET` 빠르게 생성하는 법:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. 의존성 설치 및 DB 초기화

```bash
# Python 패키지 설치
cd server
pip3 install -r requirements.txt

# DB 마이그레이션 (boxer.db 파일 생성됨)
python3 manage.py migrate

# 클라이언트 패키지 설치
cd ../client
npm install
```

### 4. Django admin에서 Site 설정

서버를 한 번 실행한 뒤:

```bash
cd server && python3 manage.py runserver 4000
```

`http://localhost:4000/admin` 접속 → **superuser가 없으면 먼저 생성**:

```bash
python3 manage.py createsuperuser
```

Admin에서 두 가지 설정:

1. **Sites** → `example.com` 클릭 → domain: `localhost:4000`, name: `localhost` 로 변경 → 저장
2. **Social applications** → Add → Provider: `Google`, Name: `Google`, Client id / Secret key 입력, Sites에서 `localhost:4000` 선택 → 저장

---

## 서버 실행

### 개발 서버 (백엔드 + 프론트엔드 동시)

프로젝트 루트에서:

```bash
npm run dev
```

- 백엔드: http://localhost:4000
- 프론트엔드: http://localhost:5173
- API 문서 (Swagger): http://localhost:4000/api/docs

### 따로 실행하고 싶을 때

```bash
# 백엔드만
cd server && python3 manage.py runserver 4000

# 프론트엔드만
cd client && npm run dev
```

---

## 프로젝트 구조

```
boxer/
├── package.json          # npm run dev 스크립트 (concurrently로 동시 실행)
│
├── server/               # Django 백엔드
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env              # 환경 변수 (git 제외)
│   ├── boxer.db          # SQLite DB (git 제외)
│   ├── config/
│   │   ├── settings.py   # Django 설정
│   │   ├── urls.py       # URL 라우팅
│   │   ├── api.py        # Django Ninja 메인 API (라우터 조합)
│   │   └── wsgi.py
│   ├── accounts/         # 사용자 모델, JWT 인증, OAuth 뷰
│   │   ├── models.py     # AbstractUser 확장 (avatar_url 추가)
│   │   ├── auth.py       # Django Ninja용 JWTAuth (HttpBearer)
│   │   ├── views.py      # /auth/jwt/ — OAuth 완료 후 JWT 발급·리다이렉트
│   │   ├── schemas.py    # UserOut 스키마
│   │   └── api.py        # GET /api/auth/me
│   ├── projects/         # 프로젝트 CRUD
│   │   ├── models.py     # Project, ProjectMember
│   │   ├── schemas.py
│   │   └── api.py        # /api/projects/
│   └── tasks/            # 태스크 CRUD + 칸반 이동
│       ├── models.py     # Task (status, priority, sort_order)
│       ├── schemas.py
│       └── api.py        # /api/tasks/
│
└── client/               # SvelteKit 프론트엔드
    ├── svelte.config.js
    ├── vite.config.ts    # /api, /auth, /accounts → localhost:4000 프록시
    ├── src/
    │   ├── lib/
    │   │   ├── api/      # axios API 클라이언트 (auth, projects, tasks)
    │   │   ├── stores/   # auth.ts (token/user), ui.ts (viewMode)
    │   │   ├── types/    # Task, Project, User 타입 + 상수
    │   │   └── components/
    │   │       ├── Sidebar.svelte
    │   │       ├── ProjectHeader.svelte   # Board/Table 토글
    │   │       ├── KanbanBoard.svelte     # DnD 컨텍스트, 컬럼 상태 관리
    │   │       ├── KanbanColumn.svelte    # svelte-dnd-action 드롭존
    │   │       ├── TaskCard.svelte        # 드래그 카드
    │   │       ├── TaskTable.svelte       # 정렬 가능한 테이블뷰
    │   │       ├── TaskModal.svelte       # 태스크 생성 모달
    │   │       ├── TaskDetailPanel.svelte # 슬라이드 오버 상세/편집
    │   │       └── CreateProjectModal.svelte
    │   └── routes/
    │       ├── +layout.ts            # ssr = false (SPA 모드)
    │       ├── login/                # 구글 로그인 버튼
    │       ├── auth/callback/        # ?token= 받아서 localStorage 저장
    │       └── app/
    │           ├── +layout.ts        # 인증 가드 + projects/user 로드
    │           └── project/[projectId]/
    │               ├── +page.ts      # tasks 로드 (depends로 캐시 키 설정)
    │               └── +page.svelte  # 칸반 또는 테이블 렌더링
    └── ...
```

---

## API 엔드포인트

전체 인터랙티브 문서: **http://localhost:4000/api/docs**

| Method | 경로 | 설명 |
|--------|------|------|
| GET | `/api/auth/me` | 현재 로그인 사용자 정보 |
| GET | `/api/projects/` | 내가 속한 프로젝트 목록 |
| POST | `/api/projects/` | 프로젝트 생성 |
| GET | `/api/projects/{id}` | 프로젝트 상세 |
| PATCH | `/api/projects/{id}` | 프로젝트 수정 (owner만) |
| DELETE | `/api/projects/{id}` | 프로젝트 삭제 (owner만) |
| GET | `/api/projects/{id}/members` | 프로젝트 멤버 목록 |
| GET | `/api/tasks/project/{projectId}` | 태스크 목록 |
| POST | `/api/tasks/project/{projectId}` | 태스크 생성 |
| GET | `/api/tasks/{id}` | 태스크 상세 |
| PATCH | `/api/tasks/{id}` | 태스크 수정 (제목/설명/상태/우선순위) |
| PATCH | `/api/tasks/{id}/move` | 태스크 이동 (드래그앤드롭용, `status` + `sort_order`) |
| DELETE | `/api/tasks/{id}` | 태스크 삭제 |

모든 API는 `Authorization: Bearer <JWT>` 헤더 필요.

---

## 태스크 상태 / 우선순위

**상태 (status)**
| 값 | 표시 |
|----|------|
| `backlog` | Backlog |
| `todo` | Todo |
| `in_progress` | In Progress |
| `done` | Done |
| `confirmed` | Confirmed |
| `cancelled` | Cancelled |

**우선순위 (priority)**
| 값 | 표시 |
|----|------|
| `urgent` | 🔴 Urgent |
| `high` | 🟠 High |
| `medium` | 🟡 Medium |
| `low` | 🔵 Low |
| `none` | ⚪ None |

---

## 인증 흐름

```
1. 클라이언트 → /accounts/google/login/
2. Google 로그인 → /accounts/google/login/callback/ (allauth 처리)
3. allauth → Django 세션 생성 → /auth/jwt/ 리다이렉트
4. /auth/jwt/ → JWT 발급 → 세션 제거 → http://localhost:5173/auth/callback?token=<JWT>
5. SvelteKit → token을 localStorage 저장 → /app 이동
6. 이후 모든 API 요청: Authorization: Bearer <JWT>
```

---

## 개발 시 알아둘 것

### 새 마이그레이션이 필요한 경우

모델을 수정했을 때:

```bash
cd server
python3 manage.py makemigrations
python3 manage.py migrate
```

### DB 초기화

```bash
cd server
rm boxer.db
python3 manage.py migrate
python3 manage.py createsuperuser  # admin 다시 생성 필요
```

### 칸반 sort_order 방식

태스크는 `sort_order: float` 필드로 순서를 관리한다. 드래그앤드롭 시 앞뒤 태스크의 중간값으로 새 순서를 계산 (`(prev + next) / 2`). 별도 재정렬 없이 단건 UPDATE로 처리된다.

### SvelteKit 데이터 갱신

태스크 생성·수정·삭제 후 `invalidate('tasks:{projectId}')` 호출 → `+page.ts`의 `depends()` 키와 매칭되어 자동 리로드.

### svelte-dnd-action 이벤트 (Svelte 5)

Svelte 5 runes 모드에서는 이벤트 핸들러를 `on:consider` 대신 `onconsider` 형태로 써야 한다 (구문 혼용 불가).

```svelte
<div
  use:dndzone={{ items, type: 'task' }}
  onconsider={(e: CustomEvent) => ...}
  onfinalize={(e: CustomEvent) => ...}
>
```

### 환경 변수 전체 목록 (`server/.env`)

```env
SECRET_KEY=         # Django SECRET_KEY (필수)
JWT_SECRET=         # JWT 서명 키 (필수)
GOOGLE_CLIENT_ID=   # Google OAuth Client ID (필수)
GOOGLE_CLIENT_SECRET= # Google OAuth Client Secret (필수)
DEBUG=True          # False로 바꾸면 프로덕션 모드
CLIENT_URL=http://localhost:5173  # CORS 허용 Origin
ALLOWED_HOSTS=localhost,127.0.0.1
```

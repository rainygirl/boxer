# 📦 Boxer

> 🇰🇷 칸반 보드, 목록 뷰, 멤버 관리, 알림, Google OAuth 로그인을 갖춘 오픈소스 프로젝트 관리 도구.
>
> 🇺🇸 Open source project management tool with Kanban board, list view, member management, notifications, and Google OAuth login.
>
> 🇪🇸 Herramienta de gestión de proyectos de código abierto con tablero Kanban, vista de lista, gestión de miembros, notificaciones e inicio de sesión con Google OAuth.
>
> 🇫🇷 Outil de gestion de projets open source avec tableau Kanban, vue liste, gestion des membres, notifications et connexion Google OAuth.
>
> 🇯🇵 カンバンボード、リストビュー、メンバー管理、通知、Google OAuthログインを備えたオープンソースのプロジェクト管理ツール。
>
> 🇨🇳 开源项目管理工具，支持看板视图、列表视图、成员管理、通知和 Google OAuth 登录。
>
> 🇹🇼 開源專案管理工具，支援看板檢視、清單檢視、成員管理、通知與 Google OAuth 登入。
>
> 🇭🇰 開源項目管理工具，支持睇板、清單、成員管理、通知同 Google OAuth 登入。
>
> 🇻🇳 Công cụ quản lý dự án mã nguồn mở với bảng Kanban, chế độ xem danh sách, quản lý thành viên, thông báo và đăng nhập Google OAuth.
>
> 🇮🇩 Alat manajemen proyek open source dengan papan Kanban, tampilan daftar, manajemen anggota, notifikasi, dan login Google OAuth.

---

## Supported Languages

- 🇰🇷 한국어
- 🇺🇸 English
- 🇪🇸 Español
- 🇫🇷 Français
- 🇯🇵 日本語
- 🇨🇳 简体中文
- 🇹🇼 繁體中文
- 🇭🇰 粵語
- 🇻🇳 Tiếng Việt
- 🇮🇩 Bahasa Indonesia

---

## Tech Stack

- **Backend** — Django 6 + Django Ninja + SQLite
- **Frontend** — SvelteKit + Svelte 5 (runes) + Tailwind CSS
- **Auth** — Google OAuth 2.0 (django-allauth) → JWT
- **Drag & Drop** — svelte-dnd-action

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm 9+
- A Google Cloud project with OAuth 2.0 credentials

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/boxer.git
cd boxer
```

### 2. Set up Google OAuth credentials

Go to [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**.

- Application type: `Web application`
- Add the following to **Authorized redirect URIs**:
  ```
  http://localhost:4000/accounts/google/login/callback/
  ```
- Copy the **Client ID** and **Client Secret** — you'll need them in the next step.

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` (project root) and fill in the required values:

```env
SECRET_KEY=<a-long-random-string>
JWT_SECRET=<another-long-random-string>
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
```

> **Security notes**
> - `SECRET_KEY` and `JWT_SECRET` must be long, random, and **different from each other**.
> - Generate them with:
>   ```bash
>   python3 -c "import secrets; print(secrets.token_hex(50))"
>   ```
> - **Never commit `.env` to version control.** It is already listed in `.gitignore`. Only `.env.example` (which contains no real secrets) should be committed.
> - Set `DEBUG=False` in any environment accessible from the internet.

### 4. Install dependencies

```bash
npm run setup
```

This runs the following in sequence:
- `pip3 install -r server/requirements.txt`
- `python3 manage.py migrate` (creates `server/boxer.db`)
- `npm install` inside `client/`

Or run each step manually:

```bash
# Backend
cd server
pip3 install -r requirements.txt
python3 manage.py migrate

# Frontend
cd ../client
npm install
```

### 5. Create a Django superuser

```bash
cd server
python3 manage.py createsuperuser
```

### 6. Configure the Django admin

Start the server temporarily:

```bash
cd server
python3 manage.py runserver 4000
```

Open `http://localhost:4000/admin` and log in with the superuser you just created.

**Sites**
- Go to **Sites** → click the default entry (`example.com`)
- Set **Domain name** to `localhost:4000`
- Set **Display name** to `localhost`
- Save

**Social Applications**
- Go to **Social applications** → **Add social application**
- Provider: `Google`
- Name: `Google`
- Client id: *(paste your Google Client ID)*
- Secret key: *(paste your Google Client Secret)*
- Under **Sites**, move `localhost:4000` to **Chosen sites**
- Save

---

## Running the dev server

From the project root, start both backend and frontend with a single command:

```bash
npm run dev
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:4000 |
| API docs (Swagger) | http://localhost:4000/api/docs |
| Django admin | http://localhost:4000/admin |

To run them separately:

```bash
# Backend only
cd server && python3 manage.py runserver 4000

# Frontend only
cd client && npm run dev
```

---

## Project Structure

```
boxer/
├── package.json              # Root dev scripts (concurrently)
├── .env                      # Local secrets — NOT committed (gitignored)
├── .env.example              # Template — safe to commit
│
├── server/                   # Django backend
│   ├── manage.py
│   └── requirements.txt
│   ├── boxer.db              # SQLite database — NOT committed
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── api.py            # Django Ninja router root
│   ├── accounts/             # User model, JWT auth, OAuth callback
│   ├── projects/             # Project + member CRUD
│   ├── tasks/                # Task CRUD + kanban move
│   └── notifications/        # In-app notifications
│
└── client/                   # SvelteKit frontend
    ├── vite.config.ts         # Proxy: /api, /auth, /accounts → :4000
    └── src/
        ├── lib/
        │   ├── api/           # Axios API clients
        │   ├── components/    # UI components (Sidebar, Kanban, Table, …)
        │   ├── i18n/          # Translations (10 languages)
        │   ├── stores/        # Svelte stores (auth, theme, ui)
        │   └── types/         # TypeScript types
        └── routes/
            ├── login/         # Google login page
            ├── auth/callback/ # Receives JWT from backend
            └── app/           # Protected area (auth guard)
                ├── project/[projectId]/
                ├── my-issues/
                ├── notifications/
                └── members/
```

---

## API Reference

Full interactive docs available at `http://localhost:4000/api/docs`.

All endpoints require `Authorization: Bearer <JWT>`.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/auth/me` | Get current user |
| PATCH | `/api/auth/me` | Update profile (nickname) |
| GET | `/api/projects/` | List projects |
| POST | `/api/projects/` | Create project |
| PATCH | `/api/projects/{id}` | Update project (owner only) |
| DELETE | `/api/projects/{id}` | Delete project (owner only) |
| GET | `/api/projects/{id}/members` | List members |
| POST | `/api/projects/{id}/members` | Invite member by email |
| PATCH | `/api/projects/{id}/members` | Change member role |
| DELETE | `/api/projects/{id}/members` | Remove member |
| GET | `/api/tasks/project/{projectId}` | List tasks |
| POST | `/api/tasks/project/{projectId}` | Create task |
| PATCH | `/api/tasks/{id}` | Update task |
| PATCH | `/api/tasks/{id}/move` | Move task (drag & drop) |
| DELETE | `/api/tasks/{id}` | Delete task |
| GET | `/api/notifications/` | List notifications |
| PATCH | `/api/notifications/{id}/read` | Mark as read |
| POST | `/api/notifications/read-all` | Mark all as read |

---

## Authentication Flow

```
1. Browser  →  /accounts/google/login/
2. Google login  →  /accounts/google/login/callback/  (allauth)
3. allauth creates Django session  →  redirects to /auth/jwt/
4. /auth/jwt/ issues JWT, clears session
         →  redirects to http://localhost:5173/auth/callback?token=<JWT>
5. SvelteKit stores token in localStorage  →  navigates to /app
6. All subsequent API calls send  Authorization: Bearer <JWT>
```

---

## Development Notes

### Apply model changes

```bash
cd server
python3 manage.py makemigrations
python3 manage.py migrate
```

### Reset the database

```bash
cd server
rm boxer.db
python3 manage.py migrate
python3 manage.py createsuperuser
# Then redo the Django admin steps (Sites + Social Applications)
```

### Environment variables reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django cryptographic signing key |
| `JWT_SECRET` | Yes | JWT token signing key |
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | Google OAuth client secret |
| `DEBUG` | No | `True` (default) or `False` for production |
| `ALLOWED_HOSTS` | No | Comma-separated hostnames (default: `localhost,127.0.0.1`) |
| `CLIENT_URL` | No | Frontend origin for CORS (default: `http://localhost:5173`) |
| `R2_ACCOUNT_ID` | No | Cloudflare R2 account ID (file attachments) |
| `R2_ACCESS_KEY_ID` | No | Cloudflare R2 access key |
| `R2_SECRET_ACCESS_KEY` | No | Cloudflare R2 secret key |
| `R2_BUCKET_NAME` | No | R2 bucket name (default: `boxer`) |
| `R2_PUBLIC_URL` | No | Public URL of the R2 bucket |

---

## License

MIT

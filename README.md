# 📦 Boxer

🇰🇷 칸반 보드, 목록 뷰, 멤버 관리, 알림, Google OAuth 로그인을 갖춘 오픈소스 설치형 이슈 트래커.

🇺🇸 Open source self-hosted issue tracker with Kanban board, list view, member management, notifications, and Google OAuth login.

🇪🇸 Rastreador de incidencias de código abierto autoalojado con tablero Kanban, vista de lista, gestión de miembros, notificaciones e inicio de sesión con Google OAuth.

🇫🇷 Outil de suivi d'incidents open source auto-hébergé avec tableau Kanban, vue liste, gestion des membres, notifications et connexion Google OAuth.

🇯🇵 カンバンボード、リストビュー、メンバー管理、通知、Google OAuthログインを備えたオープンソースのセルフホスト型イシュートラッカー。

🇨🇳 开源自托管问题追踪工具，支持看板视图、列表视图、成员管理、通知和 Google OAuth 登录。

🇹🇼 開源自托管問題追蹤工具，支援看板檢視、清單檢視、成員管理、通知與 Google OAuth 登入。

🇭🇰 開源自架問題追蹤工具，支援睇板、清單、成員管理、通知同 Google OAuth 登入。

🇻🇳 Công cụ theo dõi sự cố mã nguồn mở tự lưu trữ với bảng Kanban, chế độ xem danh sách, quản lý thành viên, thông báo và đăng nhập Google OAuth.

🇮🇩 Pelacak isu open source yang dapat dihosting sendiri dengan papan Kanban, tampilan daftar, manajemen anggota, notifikasi, dan login Google OAuth.

**Demo:** https://boxer.coroke.net

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

## Features

**Tasks**
- Kanban board and table list view with drag-and-drop reordering
- 6 status types · 5 priority levels · assignee · due date
- Subtasks with completion percentage display
- Task dependencies (blocks / blocked by) with circular dependency detection
- File attachments via Cloudflare R2 (up to 50 MB per file)
- Activity history log tracking all changes with user attribution
- Comments with @mention support
- Auto-numbered task references (e.g. `PROJ-42`)

**Projects**
- Multiple projects with custom name, color, and key
- Configurable kanban columns (show/hide per project)
- Favorite projects for quick access
- Reports: status distribution, cycle time, assignee workload, 30-day progress chart

**Team**
- Invite members by email · role management (owner / member / viewer)
- Global members directory across all projects
- Per-member issue view

**Notifications**
- In-app notifications for task assignment and @mentions
- Unread badge · mark all as read

**Search**
- Global search across all tasks by title or reference

**GitHub Integration**
- Connect a GitHub repository to each project
- Incoming webhooks: commits and pull requests referencing task IDs (e.g. `PROJ-42`) are logged in the activity history
- Auto-close tasks on PR merge using keywords: `fixes`, `closes`, or `resolves` followed by the task reference

**Outgoing Webhooks**
- Per-project outgoing webhook endpoints with custom URL, secret, and event filter
- Events: `task.created`, `task.updated`, `task.status_changed`, `task.comment`
- HMAC-SHA256 signatures via `X-Boxer-Signature-256` header for payload verification
- Dispatched asynchronously (non-blocking fire-and-forget)

**UX**
- Dark mode (light / blue / black themes)
- Fully responsive (mobile sidebar, adaptive layout)
- 10 languages supported

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
git clone https://github.com/rainygirl/boxer.git
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
1. Creates a Python virtual environment at `.venv`
2. Installs Python packages via `.venv/bin/pip3`
3. Runs `python3 manage.py migrate` (creates `server/boxer.db`)
4. Runs `npm install` inside `client/`

No need to manually activate the virtual environment — all scripts use `.venv` automatically.

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
| `BACKEND_URL` | No | Internal Django URL for SvelteKit → Django webhook proxy (default: `http://127.0.0.1:4000`) |
| `DISABLE_FILE_UPLOAD` | No | Set to `True` to disable file uploads across the entire app (default: `False`) |
| `DEMO_MODE` | No | Set to `True` to auto-add every logged-in user to the demo project and redirect them to it on entry (default: `False`) |
| `DEMO_PROJECT_ID` | No | UUID of the project to use as the demo workspace (required when `DEMO_MODE=True`) |
| `R2_ACCOUNT_ID` | No | Cloudflare R2 account ID (file attachments) |
| `R2_ACCESS_KEY_ID` | No | Cloudflare R2 access key |
| `R2_SECRET_ACCESS_KEY` | No | Cloudflare R2 secret key |
| `R2_BUCKET_NAME` | No | R2 bucket name (default: `boxer`) |
| `R2_PUBLIC_URL` | No | Public URL of the R2 bucket |

---

## Contributing

🇰🇷 기여를 환영합니다! 새로운 기능, UI 개선, 워크플로우 아이디어 등 Boxer를 더 좋게 만들 수 있다고 생각하는 것이라면 무엇이든 코드로 제안해 주세요. 정해진 범위는 없습니다. 창의적인 아이디어가 있다면 PR로 자유롭게 올려주세요.

🇺🇸 Contributions are welcome! Feel free to open a PR with any ideas you'd like to explore — new features, UI improvements, workflow enhancements, or anything else you think would make Boxer better. There's no strict scope; if you have a creative idea, bring it as code.

🇪🇸 ¡Las contribuciones son bienvenidas! Siéntete libre de abrir un PR con cualquier idea que quieras explorar: nuevas funcionalidades, mejoras de UI, flujos de trabajo u otras ideas que creas que mejorarían Boxer. No hay un alcance estricto; si tienes una idea creativa, preséntala como código.

🇫🇷 Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une PR avec vos idées — nouvelles fonctionnalités, améliorations de l'interface, flux de travail ou tout ce qui pourrait améliorer Boxer. Il n'y a pas de périmètre strict ; si vous avez une idée créative, proposez-la sous forme de code.

🇯🇵 コントリビューションを歓迎します！新機能、UIの改善、ワークフローのアイデアなど、Boxerをより良くするためのアイデアがあれば、コードとしてPRを送ってください。範囲に制限はありません。クリエイティブなアイデアがあれば、ぜひ提案してください。

🇨🇳 欢迎贡献！无论是新功能、UI 改进、工作流优化，还是任何你认为能让 Boxer 更好的想法，都欢迎以代码形式提交 PR。没有严格的范围限制，如果你有创意想法，尽管提出来吧。

🇹🇼 歡迎貢獻！無論是新功能、UI 改進、工作流程優化，或任何你認為能讓 Boxer 更好的想法，都歡迎以程式碼形式提交 PR。沒有嚴格的範圍限制，有創意的想法儘管提出來吧。

🇭🇰 歡迎貢獻！無論係新功能、UI 改進、工作流程優化，定係任何你覺得可以令 Boxer 更好嘅想法，都歡迎以程式碼形式提交 PR。冇嚴格嘅範圍限制，有創意嘅想法儘管提出嚟囉。

🇻🇳 Đóng góp luôn được chào đón! Hãy thoải mái mở PR với bất kỳ ý tưởng nào bạn muốn thử — tính năng mới, cải tiến giao diện, luồng công việc hay bất cứ điều gì bạn nghĩ sẽ giúp Boxer tốt hơn. Không có phạm vi cứng nhắc; nếu bạn có ý tưởng sáng tạo, hãy đưa nó vào code.

🇮🇩 Kontribusi sangat disambut! Silakan buka PR dengan ide apa pun yang ingin kamu eksplorasi — fitur baru, peningkatan UI, alur kerja, atau hal lain yang menurutmu bisa membuat Boxer lebih baik. Tidak ada batasan ketat; jika kamu punya ide kreatif, sampaikan dalam bentuk kode.

---

## License

MIT

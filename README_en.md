# WebControl Studio

Lightweight platform to create static marketing sites for local businesses, manage their content through a Windster-based dashboard, and publish them straight to GitHub Pages. The repository now only ships the pieces required to run the app.

## Highlights

- Visual editor with product cards, galleries and image uploads.
- Opinionated templates for five business verticals (handicrafts, food, home services, beauty, goat farming).
- Role-based access control (superadmin, admin, owner) with avatar management and last-login tracking.
- Site analytics surfaced inside the dashboard.
- Automatic publishing through the GitHub API (push to `gh-pages`, optional `CNAME`).

## Requirements

- Python 3.11+
- pip/virtualenv available in your shell
- GitHub account with a classic personal access token (`repo` + `workflow` scopes)
- Linux, macOS or WSL2 (Windows works via PowerShell + `start.bat`)

## Quick start

```bash
git clone https://github.com/AnSan29/webControl.git
cd webControl
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Environment variables

Use `.env.example` as a template for `.env`.

| Key | Description |
| --- | --- |
| `SECRET_KEY` | Secret used to sign JWT/CSRF tokens. |
| `HOST` / `PORT` | Host and port served by Uvicorn. |
| `GITHUB_TOKEN` | Personal token to push generated sites. |
| `GITHUB_USERNAME` | GitHub account that will host the pages. |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Seed credentials for the superadmin account. |
| `DATABASE_URL` | Defaults to `sqlite:///./backend/db.sqlite3`. |

### Initialize the database

```bash
source .venv/bin/activate
python - <<'PY'
from backend.database import init_db
init_db()
PY
```

## Run the backend

```bash
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` and sign in with `admin@webcontrol.com` / `admin123`. Change the password as soon as possible.

`start.sh` (Linux/macOS) and `start.bat` (Windows) wrap the same commands for quick demos.

## Tests

```bash
source .venv/bin/activate
pytest tests
```

SQLite fixtures live under `tests/test_db.sqlite3` so the main database remains untouched.

## Minimal layout

```
backend/          # FastAPI app, ORM models and seeders
frontend/         # Windster HTML + static assets
templates_base/   # Jinja templates fed with dynamic content
scripts/          # Helper utilities for imports/audits
tests/            # Pytest suite
uploads/          # User-uploaded assets served from /images
requirements.txt  # Backend dependencies
start.sh|.bat     # Convenience launchers
verify.sh         # Optional health-check script
```

All legacy docs, QA artifacts and third-party themes were removed to keep `main` lean.

## Standard workflow

1. Authenticate as superadmin.
2. Create a site by choosing one of the built-in models.
3. Customize copy, galleries and palette with the visual editor.
4. Upload assets (logos, banners) via `/api/upload-image`; they are stored under `uploads/` and exposed as `/images/<filename>`.
5. Publish from the dashboard. The backend pushes the rendered site to the customer repository (branch `gh-pages`).
6. Review analytics and last-logins to keep track of activity.

## Deployment notes

- Never commit `.env` with real secrets.
- Rotate your GitHub token frequently; keep scopes minimal.
- Protect Uvicorn with a reverse proxy (Nginx, Caddy, Traefik) and TLS.
- Back up `backend/db.sqlite3` and `uploads/` if you need to retain customer data.

## License & support

Released under the MIT license. Please open an issue or pull request on GitHub if you need help or want to contribute.

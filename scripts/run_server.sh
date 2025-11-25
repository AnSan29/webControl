#!/usr/bin/env bash

# Lightweight runner for the webControl app
# - Activates virtualenv (.venv or venv)
# - Exports .env variables if present
# - Starts uvicorn in production-mode (no --reload)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# Prefer .venv (used in repo), fallback to venv
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ] && [ -d "venv" ]; then
  VENV_DIR="venv"
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Virtualenv not found. Creating .venv and installing requirements..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
else
  source "$VENV_DIR/bin/activate"
fi

# Optional: load .env if present
if [ -f ".env" ]; then
  # shellcheck disable=SC1090
  export $(grep -v '^#' .env | xargs -d '\n' 2>/dev/null || true)
fi

# Run uvicorn (production recommended with process manager in front)
# - Use workers=4 by default, but let env override via WEB_WORKERS
WEB_WORKERS=${WEB_WORKERS:-4}
UVICORN_HOST=${HOST:-0.0.0.0}
UVICORN_PORT=${PORT:-8000}

exec uvicorn backend.main:app --host "$UVICORN_HOST" --port "$UVICORN_PORT" --workers "$WEB_WORKERS" --log-level info

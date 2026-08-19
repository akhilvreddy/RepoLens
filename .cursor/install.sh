#!/usr/bin/env bash
# Idempotent Cloud Agent install for RepoLens (FastAPI backend + Next.js frontend).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# The default image ships Python 3.12 but not the venv module. Install it once
# (idempotent: skipped when already present).
if ! python3 -c "import ensurepip" >/dev/null 2>&1; then
  echo "==> Installing python3-venv (missing ensurepip)"
  sudo apt-get update -qq
  sudo apt-get install -y -qq python3.12-venv
fi

echo "==> Backend: Python virtualenv + dependencies"
cd "$repo_root/backend"
[ -f .env ] || cp .env.example .env
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

echo "==> Frontend: Node dependencies"
cd "$repo_root/frontend"
[ -f .env.local ] || cp .env.local.example .env.local
npm ci

echo "==> Install complete"

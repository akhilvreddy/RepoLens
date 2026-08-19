# AGENTS.md

RepoLens is an AI-powered GitHub repository intelligence tool. It has two services:

- `backend/` — FastAPI service (Python 3.12) that fetches GitHub data, computes deterministic metrics, and serves AI overview/chat. Uses SQLite (`backend/repolens.db`, auto-created on startup).
- `frontend/` — Next.js (App Router, TypeScript, Tailwind) dashboard UI.

Standard setup/run/test commands live in `README.md`, `backend/README.md`, and `frontend/README.md`, and in `frontend/package.json` scripts. Prefer those as the source of truth.

## Cursor Cloud specific instructions

The update script provisions dependencies (Python venv at `/workspace/.venv`, `pip install -r backend/requirements.txt`, and `npm install` in `frontend/`). It also copies `backend/.env` and `frontend/.env.local` from the committed `.example` files if they are missing. You do NOT need to reinstall dependencies at session start.

Running the services (do NOT put these in the update script; start them manually, e.g. in tmux):

- Backend: `source /workspace/.venv/bin/activate && cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` (health check: `GET http://localhost:8000/health`).
- Frontend: `cd frontend && npm run dev` (serves on `http://localhost:3000`; expects backend at `http://localhost:8000` via `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local`).

Non-obvious notes:

- No API keys are required to run or demo. `GITHUB_TOKEN` and `OPENAI_API_KEY` are optional; without a GitHub token you rely on unauthenticated GitHub rate limits (~60 req/hr), and without an OpenAI key the AI overview/chat use a deterministic fallback. Analyzing a repo (e.g. `https://github.com/octocat/Hello-World`) works fully end-to-end without either.
- Tests: frontend uses Vitest — run `npm test -- --run` in `frontend/`. The backend has pytest configured (`backend/pyproject.toml`) but currently ships no test files, so `pytest` collects 0 tests (this is expected, not a failure).
- Lint: `npm run lint` is currently broken because the repo pins `next` to `latest` (resolves to Next.js 16), which removed the `next lint` command, and there is no standalone ESLint flat config in the repo. Do not rely on `npm run lint` until an ESLint config is added.

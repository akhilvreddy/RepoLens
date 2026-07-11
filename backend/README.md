# RepoLens Backend

RepoLens backend is a FastAPI service that:
- validates and parses GitHub repository URLs,
- fetches repository metadata, commits, contributors, issues, PRs, releases, and tree data asynchronously from GitHub,
- computes deterministic engineering metrics (activity, maintenance, contributor distribution, issue health, etc.),
- generates structured AI overview payloads through OpenAI, with graceful fallback,
- indexes selected files for grounded repository chat.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Core Layout

- `app/api`: FastAPI routes and dependencies.
- `app/core`: global settings, logging, and exceptions.
- `app/db`: SQLAlchemy models and database session.
- `app/schemas`: pydantic request/response contracts.
- `app/services`: GitHub client, deterministic metrics, OpenAI calls, retrieval/embedding, and orchestration.
- `app/repositories`: persistence helpers for repository and analysis records.
- `app/utils`: URL parsing, file filtering, chunking.

## Environment

- `GITHUB_TOKEN` optional for authenticated GitHub API calls.
- `OPENAI_API_KEY` optional for AI summary/chat calls. If absent, deterministic fallback still works.
- `ANALYSIS_CACHE_TTL_SECONDS` controls analysis cache life.
- `DATABASE_URL` defaults to SQLite at `./repolens.db`.

## API Surface

- `POST /api/repositories/analyze`
- `GET /api/repositories/{owner}/{repo}`
- `GET /api/repositories/{owner}/{repo}/metrics`
- `GET /api/repositories/{owner}/{repo}/activity`
- `GET /api/repositories/{owner}/{repo}/issues`
- `GET /api/repositories/{owner}/{repo}/contributors`
- `GET /api/repositories/{owner}/{repo}/files`
- `POST /api/repositories/{owner}/{repo}/chat`

## Notes

- Deterministic calculations are kept separate from model-driven interpretation.
- Chat and overview answers are returned only against indexed repository content.

## Future Improvements

- queue-backed analysis jobs,
- vector index persistence outside SQLite,
- richer AST-aware file intelligence.

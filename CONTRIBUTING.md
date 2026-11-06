# Contributing to RepoLens

Thanks for helping improve RepoLens. This document describes a minimal local workflow; for stack details and Cloud Agent notes, see `README.md` and `AGENTS.md`.

## Before you open a PR

1. **Backend (Python 3.12)** — from the repo root or `backend/`:

   ```bash
   cd backend && pytest
   ```

2. **Frontend (Next.js)** — from `frontend/`:

   ```bash
   npm test -- --run
   ```

## Making changes

- Prefer small, focused commits with messages that state what changed and why.
- Match existing style in the files you touch (formatting, naming, and patterns).
- If you add user-visible behavior or non-obvious API behavior, update the relevant `README.md` or route docstrings when it helps the next contributor.

## Pull requests

- Describe the problem or goal and how you verified the change (which commands you ran).
- Note any follow-ups or known limitations if they are not obvious from the code.

If anything here conflicts with team process on the hosting org, follow the team process first.

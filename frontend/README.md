# RepoLens Frontend

This is a Next.js App Router frontend that renders repository analysis and repository-grounded chat.

## Local Run

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

## Main Routes

- `/` — input form and repository examples.
- `/repositories/[owner]/[repo]` — dashboard for a single repository.

## Features in the current scaffold

- polished landing with validation and suggested inputs,
- repository header and KPI cards,
- commit and language visualizations via Recharts,
- AI overview panel,
- contributors, issues/PRs, and directory tree/README preview,
- repo-grounded chat panel with source references,
- resilient loading/error states.

## Tech

- Next.js App Router
- TypeScript
- Tailwind CSS
- Lucide icons
- Recharts

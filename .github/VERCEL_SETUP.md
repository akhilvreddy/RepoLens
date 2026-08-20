# Vercel CI setup

This repository uses `.github/workflows/vercel-deploy.yml` to deploy the `frontend/` Next.js app.

## What the workflow does

- Pull request with frontend changes -> creates a **preview deployment**.
- Push to `main` with frontend changes -> creates a **production deployment**.

## Required GitHub repository secrets

Add these in GitHub -> Settings -> Secrets and variables -> Actions -> Repository secrets:

1. `VERCEL_TOKEN`
2. `VERCEL_ORG_ID`
3. `VERCEL_PROJECT_ID`

## How to get the values

### 1) VERCEL_TOKEN

Create a personal token in Vercel:

- Vercel Dashboard -> Settings -> Tokens -> Create Token

### 2) VERCEL_ORG_ID and VERCEL_PROJECT_ID

Option A (recommended): use Vercel CLI from your machine

```bash
npx vercel login
cd frontend
npx vercel link
cat .vercel/project.json
```

Then copy:

- `orgId` -> `VERCEL_ORG_ID`
- `projectId` -> `VERCEL_PROJECT_ID`

Option B: copy IDs from Vercel project settings in the dashboard.

## Notes

- The workflow deploys from the `frontend/` directory.
- If a secret is missing, the workflow will fail early with a clear error.
- You can trigger manually from Actions via `workflow_dispatch`.

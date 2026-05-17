# Lexi Frontend

This directory contains the Next.js frontend application for Lexi.

## UI Foundation

- Component split is implemented under `app/components/`.
- shadcn-style baseline primitives live under `app/components/ui/`.
- Framer Motion powers key transitions and overlays.
- A first-run boundaries modal plus persistent reminder banner reinforces that Lexi is not legal advice.

## Implemented Workspace Flow

The current app includes the first roadmap milestones:

1. Register or log in (custom JWT auth for private MVP)
2. Return to recent user-scoped documents from the sidebar
3. Upload document (drag-and-drop or file picker)
4. Explicit consent submission (processing + optional storage)
5. Real-time processing polling with progress indicator
6. Results view (summary, classification, metadata, clauses, source excerpts)
7. Limited document-scoped Q&A with source citations and missing-information behavior
8. One-click document deletion
9. Export results via browser print/save as PDF

Backend endpoints used:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/documents`
- `POST /api/v1/documents/upload`
- `POST /api/v1/documents/{id}/consent`
- `GET /api/v1/jobs/{id}/status`
- `GET /api/v1/documents/{id}/results`
- `POST /api/v1/documents/{id}/ask`
- `DELETE /api/v1/documents/{id}`

## API Configuration

You can override the backend API base URL:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

Create `frontend/.env.local` if you want to set this locally.
For Netlify, set `NEXT_PUBLIC_API_BASE_URL` in the site environment variables to the deployed backend API URL.

Auth note: `NEXT_PUBLIC_AUTH_PROVIDER=custom` keeps the private-MVP token flow under `lexi_access_token` for local work and E2E gates. `NEXT_PUBLIC_AUTH_PROVIDER=supabase` switches the browser to Supabase-backed public-beta sessions while FastAPI remains the document-processing authority.

## Prerequisites

- Node.js 20+
- npm 10+

## Install

```bash
cd frontend
npm install
```

## Run locally

```bash
npm run dev
```

Next.js dev server runs on http://localhost:3000.

If port `3000` is busy, stop stale processes and retry:

```bash
pkill -f "next dev" || true
pkill -f "npm run dev" || true
npm run dev
```

If you are developing over SSH, a container, or WSL, make sure port `3000` is forwarded in VS Code and open the forwarded URL.

## Build

```bash
npm run build
npm run start
```

## E2E Lease Verification

Run the live full-stack browser gate:

```bash
npm run test:e2e-lease
```

This starts a live FastAPI test server on an isolated temp SQLite database and a Next.js dev server pointed at it. SQLite is used only for this fast test harness; product runtime remains Postgres.

## Deploy to Netlify

The root `netlify.toml` points Netlify at this `frontend/` directory:

- Base directory: `frontend`
- Build command: `npm run build`
- Publish directory: `.next`
- Node version: `20`

Set this Netlify environment variable before production deploys:

```bash
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.example/api/v1
```

Netlify supports modern Next.js through its OpenNext adapter, so this project does not pin `@netlify/plugin-nextjs`.

# Lexi Documentation

This directory is the documentation hub for the Lexi project.

## Directory Map

```text
docs/
├── README.md
├── media/
│   ├── samples/
│   └── screenshots/
├── product/
│   ├── roadmap.md
│   ├── styles.md
│   ├── tone.md
│   ├── user-testing.md
│   └── vision.md
└── technical/
    ├── CHANGELOG.md
    ├── contract.md
    ├── design.md
    ├── requirements.md
    ├── SETUP.md
    └── tasks.md
```

## Source of Truth

To avoid documentation drift, use these docs this way:

| Need | Read | Status |
| --- | --- | --- |
| Current product direction | `docs/product/roadmap.md` | Living |
| Current technical design and architecture | `docs/technical/design.md` | Living |
| Project-wide requirements | `docs/technical/requirements.md` | Living |
| Current engineering task board | `docs/technical/tasks.md` | Living |
| Local setup and commands | `docs/technical/SETUP.md` | Living |
| External/API integration expectations | `docs/technical/contract.md` | Living contract |
| Implementation change history | `docs/technical/CHANGELOG.md` | Append/update as milestones land |

## Quick Start Paths

- Product direction: `docs/product/vision.md`
- Delivery planning: `docs/product/roadmap.md`
- Engineering setup: `docs/technical/SETUP.md`
- API and integration contract: `docs/technical/contract.md`
- System design and architecture: `docs/technical/design.md`
- Current implementation status: `docs/technical/CHANGELOG.md`

## By Audience

### Product and Design

- `docs/product/vision.md`
- `docs/product/roadmap.md`
- `docs/product/tone.md`
- `docs/product/styles.md`
- `docs/product/user-testing.md`

### Engineering

- `docs/technical/SETUP.md`
- `docs/technical/design.md`
- `docs/technical/requirements.md`
- `docs/technical/contract.md`
- `docs/technical/tasks.md`
- `docs/technical/CHANGELOG.md`

## Current Build State (May 2026)

- Backend Docker stack runs API, worker, PostgreSQL, Redis, MinIO, and Qdrant.
- Backend migrations apply on startup.
- Frontend is a Next.js app in `frontend/` with the first MVP user flow.
- Backend API and live browser lease-verification gates pass.
- A Postgres-backed browser release gate command exists: `cd frontend && npm run test:e2e-lease:postgres`.
- RAG scaffolding, deterministic backend summaries, a local real-provider adapter, low-confidence fallback, document workspace, sidebar/history, limited Q&A, citation/missing-information behavior, unsupported-document guardrails, and the first RiskSense MVP slice exist.
- Current product screenshots live in `docs/media/screenshots/`; synthetic sample lease images live in `docs/media/samples/`.
- `docs/technical/design.md` is the canonical system design; separate architecture and data/auth notes were consolidated into it.
- Next implementation focus: improve Lexi’s output reliability and usefulness before expanding extraction edge-case unit coverage.

## Notes

- If you are setting up the app locally, start with `docs/technical/SETUP.md`.
- Use `mamba` for faster Python environment setup when available; `conda` remains supported.
- The frontend setup commands are documented in both `frontend/README.md` and `docs/technical/SETUP.md`.

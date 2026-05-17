# Lexi Backend

This directory contains the FastAPI backend, Celery worker, document processing pipeline, persistence layer, and AI/RAG services for Lexi.

## Service Foundation

- FastAPI serves the REST API under `backend/api/v1/`.
- Celery runs document processing jobs in `backend/tasks/`.
- SQLAlchemy models and Alembic migrations define users, documents, metadata, summaries, clauses, and RiskSense signals.
- PostgreSQL is the product database; SQLite is used only by fast isolated test harnesses.
- Redis backs Celery job coordination.
- MinIO/S3-compatible storage holds uploaded documents when persistent storage is enabled.
- Qdrant stores vector embeddings for retrieval-backed document Q&A.

## Implemented Document Flow

The current backend supports the first MVP lifecycle:

1. Register or log in with private-MVP custom JWT auth
2. Upload a supported document file
3. Record explicit processing and optional storage consent
4. Extract text from PDF, DOCX, JPEG, or PNG input
5. Classify supported Ontario residential leases
6. Extract metadata and clauses
7. Generate grounded summaries with conservative fallback behavior
8. Index document chunks for retrieval
9. Return source excerpts, document-scoped Q&A, and RiskSense signals
10. Delete documents and associated records through the API

Core endpoints:

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

## Configuration

Start from the repository root `.env.example`. The most important backend values are:

```bash
DATABASE_URL=postgresql://lexi:lexi@localhost:5432/lexi
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
S3_ENDPOINT_URL=http://localhost:9000
QDRANT_URL=http://localhost:6333
AUTH_PROVIDER=custom
LLM_PROVIDER=fake
```

Auth note: `AUTH_PROVIDER=custom` keeps local/private-MVP JWT endpoints active. `AUTH_PROVIDER=supabase` disables custom token issuance and verifies Supabase JWTs while preserving server-side document ownership checks.

LLM note: `LLM_PROVIDER=fake` keeps tests and local gates deterministic. The Ollama-compatible provider is available for local real-provider experiments without paid APIs.

## Prerequisites

- Python 3.11
- Docker Compose
- Tesseract OCR
- Poppler for image/PDF OCR helpers
- `mamba` or `conda` for the recommended project environment

## Install

From the repository root:

```bash
./scripts/onboarding/setup-dev.sh
```

Or install the backend dependencies directly:

```bash
make -f backend/Makefile conda-setup
```

## Run Locally

Start the full backend stack:

```bash
docker compose up -d --build api worker
```

The API runs on http://localhost:8000.

Check health:

```bash
curl http://localhost:8000/health
```

For direct local API development outside Docker:

```bash
make -f backend/Makefile run-api
make -f backend/Makefile run-worker
```

## Migrations

Apply existing migrations:

```bash
alembic -c backend/alembic.ini upgrade head
```

Create a new migration after model changes:

```bash
make -f backend/Makefile db-migrate message="Describe change"
```

Docker startup applies migrations before the API process starts.

## Tests

Run backend tests in the project environment:

```bash
make -f backend/Makefile test-conda
```

Or run pytest directly:

```bash
pytest backend/tests/ -v --cov=backend
```

The current roadmap intentionally defers additional extraction edge-case unit tests while Lexi’s summary, Q&A, and RiskSense output quality is sharpened.

## Local Development Notes

- Use `docs/technical/SETUP.md` for the full setup and troubleshooting guide.
- Use `docs/technical/design.md` for the canonical backend architecture.
- Use `docs/technical/contract.md` for frontend/API integration expectations.
- Keep generated uploads, local databases, coverage output, and build caches out of git.

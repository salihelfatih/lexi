# Lexi Setup Guide

## Prerequisites

- Mamba or Conda for the local Python environment
  - Recommended: Miniforge/Mambaforge with `mamba` for faster dependency solving
  - Fallback: Anaconda or Miniconda with `conda`
- Docker and Docker Compose
- npm / Node.js for the frontend

Tesseract and Poppler are installed inside the backend Docker image. Install them locally only if you run OCR outside Docker.

## Installation

### Fast Contributor Onboarding

If you want the fastest path for local setup, run:

```bash
./scripts/onboarding/setup-dev.sh
```

Then start services:

```bash
./scripts/onboarding/start-dev.sh
```

Then verify health:

```bash
./scripts/onboarding/check-health.sh
python3 scripts/onboarding/validate-setup.py
```

For manual setup, follow the detailed steps below.

### 1. Create Mamba/Conda Environment

Mamba is recommended because the ML dependencies are large and solve faster:

```bash
# Preferred
mamba env create -f environment.yml

# Fallback
conda env create -f environment.yml

# Activate environment
conda activate lexi

# Install the pinned spaCy model
python -m pip install \
  https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

For existing environments:

```bash
mamba env update -n lexi -f environment.yml --prune

# Fallback
conda env update -n lexi -f environment.yml --prune
```

If `mamba` is installed but your shell cannot find it, make sure Miniforge is on PATH:

```bash
export PATH="$HOME/.local/miniforge3/bin:$PATH"
```

The onboarding script also checks common Miniforge/Mambaforge install paths automatically.

### 2. Start Docker Backend

```bash
# Builds and starts API, worker, PostgreSQL, Redis, MinIO, and Qdrant
docker compose up -d --build api worker

# Or:
make -f backend/Makefile docker-backend
```

The API container applies database migrations on startup. MinIO bucket creation is handled by the `minio-init` service.

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add the key to .env as MASTER_ENCRYPTION_KEY
```

Docker Compose overrides local service URLs for containers. `.env` is still useful for local tooling and future deployment configuration.

The Docker API and worker share a named `upload_temp` volume at
`/var/lib/lexi/uploads`. Keep `UPLOAD_TEMP_DIR` aligned between both services so
the worker can read files uploaded through the API before consented processing
starts.

### Database and Auth Policy

Lexi is Postgres-first for product runtime. Docker Compose starts PostgreSQL and the API container applies Alembic migrations on startup.

SQLite is used only for fast, isolated automated tests that create throwaway databases. It is not the product database.

Private MVP auth uses Lexi's built-in custom JWT flow. Supabase Auth is the accepted public-beta path; keep `AUTH_PROVIDER=custom` and `NEXT_PUBLIC_AUTH_PROVIDER=custom` for local private-MVP work and E2E gates. Public-beta frontend builds should set `NEXT_PUBLIC_AUTH_PROVIDER=supabase`, `NEXT_PUBLIC_SUPABASE_URL`, and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` while the backend sets `AUTH_PROVIDER=supabase` and the Supabase verification settings.

See [design.md](design.md) for the canonical data/auth design.

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

## Running the Application

### Backend

```bash
docker compose up -d --build api worker
```

API will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs
MinIO console: http://localhost:9001
Qdrant: http://localhost:6333

### Start Frontend (Next.js dev)

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

If port `3000` is busy, clear stale local dev processes and retry:

```bash
pkill -f "next dev" || true
pkill -f "npm run dev" || true
cd frontend
npm run dev
```

To build and run production locally:

```bash
cd frontend
npm run build
npm run start
```

## Testing the API

Document endpoints require authentication. Create a user and log in through the frontend or Swagger UI before uploading documents.

### 1. Upload a Document

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/lease.pdf"
```

Response:
```json
{
  "document_id": "uuid-here",
  "filename": "lease.pdf",
  "format": "pdf",
  "size_bytes": 12345,
  "message": "Document uploaded successfully. Please provide consent to proceed."
}
```

### 2. Provide Consent

```bash
curl -X POST "http://localhost:8000/api/v1/documents/{document_id}/consent" \
  -H "Content-Type: application/json" \
  -d '{
    "processing_consent": true,
    "storage_consent": false
  }'
```

### 3. Check Job Status

```bash
curl "http://localhost:8000/api/v1/jobs/{document_id}/status"
```

### 4. Get Results

```bash
curl "http://localhost:8000/api/v1/documents/{document_id}/results"
```

## Development

### Run Tests

```bash
mamba run -n lexi pytest backend/tests/ -v --cov=backend

# Or, after activation:
conda activate lexi
pytest backend/tests/ -v --cov=backend

# Or:
make -f backend/Makefile test-conda
```

Fast lease verification gates:

```bash
# Backend API + eager worker, isolated temp SQLite
conda activate lexi
pytest backend/tests/test_api.py -vv

# Live browser + live FastAPI test server + eager worker, isolated temp SQLite
cd frontend
npm run test:e2e-lease
```

These gates intentionally use SQLite for speed and isolation.

Postgres-backed release gate:

```bash
cd frontend
npm run test:e2e-lease:postgres
```

Run this gate in CI release jobs, before release cuts, and before public-beta milestones.
It starts or reuses the Docker Compose `postgres` service, creates a clean
`lexi_e2e_8011` database, applies Alembic migrations before the API starts, and
runs the same browser lease-verification flow with eager Celery and isolated temp
uploads.

If CI already provides a test Postgres instance, point the gate at it and skip
Compose startup:

```bash
cd frontend
LEXI_E2E_SKIP_DOCKER_POSTGRES=1 \
LEXI_E2E_POSTGRES_ADMIN_URL=postgresql://lexi:lexi@127.0.0.1:5432/postgres \
npm run test:e2e-lease:postgres
```

### Create Database Migration

```bash
make -f backend/Makefile db-migrate message="Add new field"

# Or manually:
alembic -c backend/alembic.ini revision --autogenerate -m "Add new field"
```

### Code Formatting

```bash
black backend/
ruff check backend/
```

## Troubleshooting

### Tesseract Not Found

If you get "tesseract not found" errors:

```bash
# Find tesseract path
which tesseract

# Set in Python (add to config.py if needed)
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection
psql postgresql://lexi:lexi@localhost:5432/lexi
```

### Redis Connection Issues

```bash
# Check Redis is running
docker ps | grep redis

# Test connection
redis-cli ping
```

### Qdrant Connection Issues

```bash
# Check Qdrant is running
docker ps | grep qdrant

# Health check
curl http://localhost:6333/healthz
```

### MinIO Connection Issues

```bash
# Check MinIO is running
docker ps | grep minio

# Access console
open http://localhost:9001
```

## Architecture

See [design.md](design.md) for the current technical map.

The short version:

- Next.js UI calls FastAPI under `/api/v1`.
- FastAPI owns document upload, consent, results, deletion, auth checks, and RAG/RiskSense API surfaces.
- Celery workers process documents asynchronously.
- PostgreSQL is the product database; SQLite is reserved for fast isolated tests.
- MinIO/S3-compatible storage handles persistent document storage.
- Qdrant currently backs vector retrieval.

## Next Steps

1. Run the backend and live browser lease-verification gates with the RiskSense assertions.
2. Run the Postgres-backed E2E release gate on Docker-enabled CI or before release cuts.
3. Evaluate RiskSense output against real Ontario lease examples.
4. Prepare user testing sessions.

## Production Considerations

Before deploying to production:

1. Set strong encryption keys
2. Configure proper authentication
3. Set up HTTPS/TLS
4. Use production-grade PostgreSQL
5. Configure Redis persistence
6. Set up proper S3 storage
7. Implement rate limiting
8. Add monitoring and logging
9. Set up backup procedures
10. Review security settings

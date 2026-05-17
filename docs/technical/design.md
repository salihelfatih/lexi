# Lexi System Design

> Canonical technical design for Lexi.
>
> Last updated: May 16, 2026

## Purpose

This document is the living system design for Lexi. It consolidates the current architecture and
data/auth strategy into one place.

Use this document for:

- implementation shape
- service boundaries
- data ownership
- auth and consent decisions
- document-processing flow
- RAG, LLM, and RiskSense boundaries
- release gate expectations

Use [requirements.md](requirements.md) for project-wide acceptance criteria,
[tasks.md](tasks.md) for active engineering work, [SETUP.md](SETUP.md) for
local commands, and [../product/roadmap.md](../product/roadmap.md) for phased
product direction.

## Product Shape

Lexi is a legal understanding system. It helps users read legal documents by
extracting text, structuring clauses, identifying key metadata, generating
grounded explanations, and eventually surfacing risk intelligence.

Lexi provides legal information, not legal advice. The system must never:

- declare legality
- predict legal outcomes
- tell users what decision to make
- invent facts outside the uploaded document
- use user documents for model training without explicit opt-in

Current MVP focus:

- Ontario residential leases
- private MVP users
- custom JWT auth
- FastAPI backend
- Next.js frontend
- Postgres product runtime
- SQLite only for fast isolated tests
- deterministic fake LLM provider for local gates

Near-term direction:

1. Run the backend and live browser gates with the RiskSense assertions active.
2. Verify the Postgres-backed E2E release gate on Docker-enabled CI or before release cuts.
3. Evaluate RiskSense against real Ontario lease examples and tune wording/thresholds.
4. Prepare user testing sessions for Ontario residential lease scenarios.

## Design Principles

1. **Consent before processing.** Uploading a file does not imply consent to
   process or store it.
2. **Postgres for product data.** Local Docker, staging, and production use
   PostgreSQL. SQLite is test-only.
3. **Ground every explanation.** Summaries and Q&A must use extracted clauses or
   retrieved document text as their source.
4. **Delete means inaccessible.** After deletion, results and job status must no
   longer be readable.
5. **Fast gates and release gates have different jobs.** SQLite gates optimize
   for speed; the Postgres gate optimizes for migration and database
   fidelity.
6. **Keep RiskSense informational.** Risk outputs prioritize attention, explain
   reasons, show confidence, and avoid legal conclusions.
7. **Move deliberately across boundaries.** Large service reorganizations should
   wait until the product proof gates are stable enough to protect the behavior.

## Current Product Gate

The primary proof point is the lease verification lifecycle:

Register/login -> upload sample lease -> consent -> eager worker processing ->
results display -> delete -> post-delete `404` for results and job status.

Current gates:

- Backend API gate: `backend/tests/test_api.py`
- Live browser gate: `frontend/tests/lease-verification-flow.test.js`

The browser gate starts a live FastAPI test server, starts Next.js against it,
uploads a generated sample PDF, processes the document eagerly, verifies the
results UI, deletes the document, and confirms deleted resources return `404`.

## Runtime Architecture

```text
Next.js UI
  |
  | REST /api/v1
  v
FastAPI API
  |
  | SQLAlchemy
  v
PostgreSQL

FastAPI API
  |
  | Celery task dispatch
  v
Celery Worker
  |
  +--> text extraction
  +--> document classification
  +--> clause parsing
  +--> metadata extraction
  +--> grounded summary generation
  +--> best-effort RAG indexing
  +--> optional persistent object storage

Object storage:
  - temporary local upload storage before/without persistent consent
  - S3-compatible storage for persistent documents

Vector storage:
  - Qdrant currently
  - pgvector remains a future option
```

## Repository Boundaries

```text
backend/
├── api/v1/
│   ├── auth.py          # custom private-MVP auth endpoints
│   ├── documents.py     # upload, consent, results, delete, ask
│   └── jobs.py          # processing status
├── core/                # compatibility/domain wrappers around services
├── services/            # current business logic implementation
├── tasks/               # Celery document processing
├── ml/
│   ├── models/          # classification wrapper
│   ├── rag/             # chunking, retrieval, vector store adapters
│   └── llm/             # providers, prompts, explanation/Q&A scaffolding
├── alembic/             # schema migrations
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic API schemas
├── config.py            # environment-backed settings
├── database.py          # engine/session setup
└── security.py          # JWT utilities

frontend/
├── app/                 # Next.js App Router app
├── app/components/      # MVP upload, consent, results, account UI
└── tests/               # Playwright browser gates
```

The current `backend/services/` implementation is acceptable for the MVP. The
`backend/core/` and `backend/ml/` wrappers give the codebase room to move toward
clearer domain boundaries gradually. Avoid a large service move solely for
tidiness while the product proof gates are still young.

## API Surface

Current first-party API endpoints:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/documents/upload`
- `POST /api/v1/documents/{document_id}/consent`
- `GET /api/v1/jobs/{document_id}/status`
- `GET /api/v1/documents/{document_id}/results`
- `DELETE /api/v1/documents/{document_id}`
- `POST /api/v1/documents/{document_id}/ask`

Near-term workspace API additions:

- `GET /api/v1/documents` for a user-scoped document history/sidebar
  returning safe document metadata and status, not extracted text
- optional persisted Q&A messages after the single-document Q&A behavior is safe

API rules:

- document endpoints require authenticated users
- documents are always scoped by owner
- processing starts only after processing consent
- storage consent controls persistent storage mode
- deleted documents must behave as inaccessible
- user-facing errors should be clear and avoid stack traces or document text

## Document Lifecycle

### 1. Auth

Private MVP auth uses the built-in custom flow:

- user registration in the `users` table
- hashed passwords
- first-party JWT access tokens
- user-scoped document queries

This is acceptable for private MVP proof and local E2E gates. It is not the
public-beta path.

### 2. Upload

Users upload a document through the API or UI. Supported formats are:

- PDF
- DOCX
- JPEG
- PNG

Uploads are validated for type and size. The default maximum file size is 50 MB.
The uploaded file is stored in temporary local storage until the user makes a
consent decision.

### 3. Consent

Consent has two independent choices:

- processing consent, required before analysis
- storage consent, optional, controls persistent storage

If processing consent is declined, Lexi deletes the uploaded document
immediately. If processing consent is granted, the backend creates a job status,
sets storage mode, records consent timestamps, and dispatches processing.

Storage mode:

- `ephemeral`: default when storage consent is not granted
- `persistent`: used only when storage consent is granted

### 4. Processing

The Celery task in `backend/tasks/processing.py` orchestrates the current
pipeline:

1. set job status to `extracting_text`
2. extract text from the uploaded file
3. persist extracted text and confidence
4. try best-effort RAG indexing
5. set job status to `classifying_document`
6. classify the document
7. when the document is an Ontario residential lease, parse clauses
8. extract metadata
9. generate a grounded summary artifact
10. generate first-pass rule-based RiskSense signals
11. when persistent mode is selected, store the document in S3-compatible storage
12. set job status to `complete`

If a step fails, the job status is set to `failed` with a safe user-facing error.

### 5. Results

Results include:

- document type
- classification confidence
- extracted metadata
- extracted clauses
- extraction confidence
- total clause count
- optional grounded summary payload
- optional RiskSense payload for supported leases

The backend already persists a `DocumentSummary` generated from clauses or
extracted text through the configured LLM provider. The current default provider
is deterministic and fake, so tests do not require network access or paid LLM
calls. A local Ollama-compatible adapter is available for real-provider
experiments. The frontend prefers this backend summary payload when present and
falls back to its structured MVP summary only when a summary artifact is
unavailable. When extraction confidence is low, Lexi stores a conservative
fallback summary instead of asking a model to infer from unclear text.

The backend also persists first-pass `RiskSignal` records for supported Ontario
leases. Each signal includes a rule ID, severity, confidence, plain-language
reason, and source clause. Results expose these through `risk_sense`, including
a calm top-risk summary and confidence rollup across extraction,
classification, metadata, and risk signals. Unsupported `unknown` documents do
not receive RiskSense output.

### 6. Deletion

Deletion removes dependent records and temporary files, attempts object-storage
cleanup when applicable, and soft-deletes the document record. After deletion,
results and job status endpoints must return `404`.

## Data Design

Lexi is Postgres-first.

Product runtime:

- local Docker
- staging
- production

Test-only runtime:

- SQLite for isolated automated tests
- temporary SQLite for the live browser lease-verification gate

SQLite must not be treated as a product database. It exists so tests can create
and destroy deterministic throwaway state without Docker.

Current main tables:

- `users`
- `documents`
- `consent_records`
- `job_statuses`
- `document_metadata`
- `document_summaries`
- `clauses`
- `risk_signals`

Current ownership model:

- `documents.user_id` identifies the authenticated owner
- document reads and deletion filter by owner and `deleted_at is null`
- consent, metadata, summaries, job status, clauses, and risk signals are tied to a document
- post-delete dependent records are removed and the document is marked deleted

Migration policy:

- Alembic owns product schema changes
- Docker API startup applies migrations
- the Postgres E2E gate must run against Alembic migrations, not
  `Base.metadata.create_all`

## Auth Design

Default private-MVP behavior is `AUTH_PROVIDER=custom`. Supabase Auth is the
accepted public-beta path. The decision is tracked in the active task board,
not a separate decision file.

Custom auth includes:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- password hashing
- JWT access tokens

Public beta path:

1. **Supabase Auth.** Supabase handles signup, login, password reset, email
   verification, refresh sessions, and future OAuth/MFA options. The frontend
   obtains a Supabase access token. FastAPI verifies Supabase JWTs through JWKS
   and maps the token subject to Lexi-owned rows.
2. **Custom auth stays private-MVP only.** Custom auth hardening is
   intentionally deferred because Supabase is the chosen public-beta path. If
   this decision is ever reversed, custom auth must add email verification,
   password reset, refresh/session handling, rate limiting, brute-force
   protection, session revocation, and safer browser token storage before
   public use.

Do not move document processing directly into browser-to-database calls. FastAPI
remains the authority for document upload, consent, processing, results,
deletion, RAG, and RiskSense.

## Storage Design

Temporary storage:

- used for uploaded files before processing and for ephemeral mode
- isolated in temp directories during tests
- cleaned up on declined consent or deletion

Persistent storage:

- requires storage consent
- uses S3-compatible object storage such as MinIO locally or AWS S3 later
- stores app metadata and processing results in Postgres

Encryption:

- `MASTER_ENCRYPTION_KEY` is required for real persistent storage
- stored documents must be encrypted at rest
- production needs real key management and rotation policy before public launch

## Extraction, Classification, and Metadata

Text extraction:

- native PDF extraction
- DOCX extraction
- OCR for scanned PDFs/images
- confidence and warning output

Classification:

- current MVP classifies Ontario residential leases vs unknown
- the implementation uses MVP-friendly rule-based behavior behind the classifier
  boundary, with Hugging Face/PyTorch remaining the intended ML direction
- low-confidence or unsupported documents should produce safe unsupported-document
  behavior
- unknown documents must not be treated as legal documents by the UI
- unknown documents should show a calm unsupported state with classification
  confidence, delete/re-upload actions, and no RiskSense or broad legal Q&A

Clause parsing:

- detects numbered, lettered, and paragraph-based clauses
- tags clause types such as termination, fees, access, maintenance, utilities,
  pets, subletting, and other
- preserves clause text for grounding

Metadata:

- lease start date
- lease end date
- tenant names
- landlord names
- rental property address
- monthly rent

Missing fields should be represented as not found rather than invented.

## RAG and LLM Design

RAG scaffolding exists:

- clause/text chunking
- embedding interface
- Qdrant vector store adapter
- retrieval helper
- document-scoped `ask` endpoint

Current RAG behavior:

- processing attempts best-effort indexing
- indexing failures do not block core processing
- deterministic in-memory retrieval and hashed embeddings support automated
  Q&A gates without Qdrant or model downloads
- `/documents/{id}/ask` retrieves chunks and returns a limited extractive answer
  with quoted source citations
- missing information produces a document-scoped uncertainty response
- optional user context is accepted but kept separate from document evidence and
  cannot override source text

Summary behavior:

- `SummaryService` builds context from clauses first, extracted text second
- provider configuration comes from environment variables
- the default fake provider is deterministic for tests
- real provider adapters should keep the same grounded interface

LLM rules:

- only use supplied context
- say when information is not in the document
- cite or quote source text where practical
- never provide legal advice
- never invent external legal rules

## RiskSense Design

RiskSense / Lexi Risk Engine has its first MVP slice implemented.

The current slice builds on stable extraction, lifecycle, summary, and retrieval
behavior and includes:

- risk severity
- confidence
- reason
- source clause
- calm top-risk summary
- confidence rollups across extraction, classification, metadata, and risk signals

The first implementation is deterministic and rule-based. It flags attention
signals for rent/payment timing, extra charge language, landlord entry, tenant
maintenance responsibility, utility responsibility, termination notice, and
subletting or assignment approval. Advanced scoring, financial impact
estimation, forecasting, comparison, and pattern detection remain future work.

RiskSense must remain informational:

- prioritize attention
- explain why something may deserve review
- show uncertainty
- avoid alarmist language
- avoid legality claims
- avoid outcome prediction

## Frontend Design Boundary

The current frontend is a Next.js MVP for:

- registration/login
- first-run boundaries modal
- upload
- consent
- processing status
- results
- print/export
- deletion

Frontend work should keep the UI calm, compact, and task-focused. The product is
an operational legal-understanding tool, not a marketing page. The first screen
should support the actual user workflow.

Phase 2 UI direction is a document-centered conversation workspace:

- the primary object is the active document, not a generic chat session
- the left sidebar lists recent user documents and their processing status
- the main surface shows upload, consent, summary, key details, source excerpts,
  and document-scoped chat for the selected document
- each Q&A answer must expose source text or citations from the active document
- optional user context can clarify the situation, but it must be visually and
  semantically separate from extracted document facts
- the chat input should not invite general legal questions without an uploaded,
  processed, supported document
- Framer Motion should be used for subtle state transitions only

Current and near-term UI work:

- user-scoped document history/sidebar exists
- backend summary payload is preferred when present
- safe extractive document-scoped Q&A UI exists inside the document workspace
- unsupported-document empty/error states for `unknown` classification exist
- RiskSense section exists for supported processed leases with source excerpts
  and confidence rollups
- move the boundaries acknowledgement toward user-scoped/server-backed tracking
  before public beta
- keep consent and deletion obvious

## Testing Design

### Fast Backend Gate

```bash
pytest backend/tests/test_api.py -vv
```

This gate uses isolated SQLite by default and proves API behavior plus eager
worker processing.

### Live Browser Gate

```bash
cd frontend
npm run test:e2e-lease
```

This gate starts:

- a live FastAPI test server
- isolated temp SQLite
- eager Celery processing
- isolated upload temp storage
- Next.js pointed at the live test API

It is the default full-stack product proof during active development.

### Postgres Gate

```bash
cd frontend
npm run test:e2e-lease:postgres
```

This gate runs the same lease-verification browser path against Docker Postgres
and Alembic migrations. It should be used in CI release jobs, before release
cuts, and before public-beta milestones, while the SQLite gate remains the fast
local default.

It:

- starts or reuses Docker Postgres
- creates a clean `lexi_e2e_8011` test database
- applies Alembic migrations before the test server starts
- keeps eager Celery mode for deterministic product proof
- isolates uploads in a temp directory
- runs the same Playwright spec as the SQLite live browser gate
- cleans up test users, documents, job statuses, metadata, summaries, clauses,
  risk signals, consent records, and temp files
- verifies post-delete results and job status return `404`
- verifies user scoping

## Operations and Configuration

Core environment variables:

- `DATABASE_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `MASTER_ENCRYPTION_KEY`
- `UPLOAD_TEMP_DIR`
- `AUTH_PROVIDER`
- `JWT_SECRET_KEY`
- `SUPABASE_URL`
- `SUPABASE_JWKS_URL`
- `SUPABASE_JWT_AUDIENCE`
- `SUPABASE_JWKS_CACHE_SECONDS`
- `QDRANT_URL`
- `LLM_PROVIDER`
- `LLM_MODEL_NAME`
- `LLM_BASE_URL`
- `LLM_SUMMARY_MIN_EXTRACTION_CONFIDENCE`

Local Docker services:

- API
- worker
- PostgreSQL
- Redis
- MinIO
- Qdrant

Production readiness still requires:

- strong secrets
- HTTPS/TLS
- production-grade PostgreSQL
- object-storage hardening
- Redis persistence/retry review
- rate limiting
- monitoring and alerting
- backup and restore procedures
- auth public-beta decision
- privacy/logging review

## Documentation Ownership

Keep this document comprehensive and current. The old split between
architecture, data/auth strategy, and design caused drift; those separate notes
have been consolidated here.

When implementation changes a system boundary, update:

1. this design document
2. [requirements.md](requirements.md), if acceptance criteria changed
3. [tasks.md](tasks.md), if task status or next work changed
4. [CHANGELOG.md](CHANGELOG.md), when a meaningful milestone lands

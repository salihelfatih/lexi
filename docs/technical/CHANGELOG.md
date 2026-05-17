# Lexi Implementation Changelog

> **Current Status (May 2026):** Active technical MVP moving toward private beta for Ontario residential leases.

---

## ✅ Phase 1: Backend MVP (Complete)

**Infrastructure**
- FastAPI REST API with async support
- Celery worker for background processing
- PostgreSQL with Alembic migrations
- Redis for job queuing
- MinIO (S3-compatible) for document storage
- Qdrant for vector embeddings
- Docker Compose local development stack

**API Endpoints**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - JWT authentication
- `GET /api/v1/auth/me` - Current user info
- `GET /api/v1/documents` - User-scoped safe document history
- `POST /api/v1/documents/upload` - Document upload
- `POST /api/v1/documents/{id}/consent` - Consent management
- `GET /api/v1/jobs/{id}/status` - Processing status
- `GET /api/v1/documents/{id}/results` - Retrieval results
- `DELETE /api/v1/documents/{id}` - Secure deletion
- `POST /api/v1/documents/{id}/ask` - Document Q&A (RAG)

**Processing Pipeline**
- Text extraction (PDF, DOCX, images with OCR via Tesseract)
- Document classification (Ontario residential leases)
- Clause parsing (8 types: termination, fees, access, penalties, maintenance, subletting, utilities, other)
- Metadata extraction (dates, names, addresses, rent amounts)
- Async job orchestration with status tracking

**Security & Privacy**
- AES-256 encryption at rest
- JWT-based authentication
- User-scoped document access
- Explicit consent workflow
- Ephemeral and persistent storage modes
- PII-protected logging
- One-click secure deletion

---

## ✅ Phase 1.5: Frontend MVP (Complete)

**UI Implementation**
- Next.js 16 with App Router and Turbopack
- React 19 with TypeScript
- Framer Motion for transitions
- shadcn-style UI primitives
- Mobile-responsive design

**User Flow**
- Registration and login with JWT tokens
- Drag-and-drop document upload
- Explicit consent submission (processing + optional storage)
- Real-time processing status with progress indicators
- Results view (summary, classification, metadata, clauses)
- One-click document deletion
- Export via browser print/save as PDF

**UX Features**
- First-run boundaries modal
- Persistent reminder banner ("Lexi is not legal advice")
- Component-based architecture for maintainability
- Theme toggle (light/dark mode)

---

## 🚧 Phase 2: RAG Pipeline (Workspace and Limited Q&A Slice Complete)

**Implemented**
- Clause-level chunking with metadata
- Transformer-based embeddings (Hugging Face)
- Deterministic hashed embeddings and in-memory vector retrieval for tests/live gates
- Qdrant vector store adapter
- Retrieval service with top-K search
- Grounded prompt templates for LLM
- Deterministic fake LLM provider for grounded summaries
- `DocumentSummary` persistence and summary response payload
- `POST /api/v1/documents/{id}/ask` endpoint
- RAG indexing in Celery pipeline
- `GET /api/v1/documents` for safe user-scoped document history/sidebar data
- Document-centered workspace with sidebar/history, active document header, upload/consent states, summary, source excerpts, and chat
- Limited document-scoped Q&A with quoted source citations, missing-information behavior, and user context kept separate from document evidence
- Unsupported-document guardrails for `unknown` classification before summaries, chat, or RiskSense appear

**Pending**
- Real LLM provider integration for full natural-language Q&A after extractive safeguards remain stable
- Confidence scoring for LLM outputs

---

## ✅ Phase 3: RiskSense / Lexi Risk Engine (First MVP Slice Complete)

**Implemented**
- Severity levels for flagged clauses
- Confidence rollups across processing stages
- Prioritized "top risks" summary
- Source-grounded rule-based attention signals for Ontario leases
- Calm workspace UI section with confidence and source excerpts

**Roadmap Features**
- Financial impact estimation
- Lease comparison
- Renewal and penalty forecasting
- Pattern detection across user documents

**Status:** First deterministic, rule-based MVP slice implemented; advanced
analytics remain planned.

---

## 🎯 Current Priorities (May 2026)

1. **Output reliability** - Make summaries, Q&A, source excerpts, and RiskSense feel more specific, grounded, and useful
2. **Real-lease evaluation** - Compare Lexi’s output against sample scenarios and real Ontario lease examples before broad user testing
3. **Deferred edge-case unit tests** - Keep extraction/unit hardening tracked, but do not let it block the output-quality pass

---

## 🛠️ Recent Infrastructure Updates

**May 2026**
- Added product screenshots to the main README and aligned tracking docs around the next output-reliability pass.
- Marked extraction edge-case unit tests as intentionally deferred while Lexi’s target output behavior is sharpened.
- Completed the User Testing Readiness prep slice: backend API gate passes in
  the `lexi` Python environment, the live browser RiskSense gate passes, 5
  Ontario lease scenarios are documented, the playbook/trackers are refreshed,
  and a private-beta checklist is available for each testing wave.
- Fixed a project-environment auth hang by keeping FastAPI auth dependencies on
  async dependency wrappers while preserving direct sync security helpers for
  unit tests.
- Simplified the frontend consent path so upload is temporary intake and the
  post-upload consent panel is the single analysis permission step; added a
  compact results readiness strip for extraction/classification confidence and
  source clause count.
- Added the first RiskSense MVP slice: persisted `risk_signals`, a deterministic
  rule-based lease risk service, confidence rollups, calm top-risk summaries,
  results API payloads, workspace UI, and safety tests that prevent generated
  legality claims or legal outcome predictions.
- Replaced the frontend private-MVP-only custom auth UI path with
  provider-aware auth: custom remains available for local/private gates, while
  `NEXT_PUBLIC_AUTH_PROVIDER=supabase` enables Supabase sign-up, sign-in,
  password reset, session refresh, and sign-out flows.
- Fixed Docker live processing for uploaded documents by sharing the upload
  temp directory between the API and worker containers. The PNG upload path now
  completes into the safe unsupported-document state instead of failing because
  the worker cannot find the API container's temp file.
- Added a failed-processing recovery state in the document workspace so users
  see a clear message and upload/delete actions instead of a disabled composer
  that still says the document is being analyzed.
- Consolidated the Supabase public-beta auth decision into the canonical task
  board and auth design docs, and removed the standalone decision file.
- Added provider-aware backend auth: `AUTH_PROVIDER=custom` keeps private MVP
  register/login working, while `AUTH_PROVIDER=supabase` disables custom token
  issuance, verifies Supabase JWTs through JWKS, and maps Supabase subjects to
  Lexi document ownership
- Added a Postgres-backed live browser release gate command:
  `cd frontend && npm run test:e2e-lease:postgres`
- Added `GET /api/v1/documents` for safe, user-scoped document history without
  exposing extracted document text
- Added deterministic in-memory vector retrieval and hashed embeddings so Q&A
  gates can run without Qdrant, model downloads, paid APIs, or network calls
- Reworked the frontend into a document-centered workspace with sidebar/history,
  active document header, source excerpts, and document-scoped Q&A
- Added limited extractive Q&A answers that quote/cite retrieved document text,
  say when an answer is not present, and keep optional user context separate
  from document evidence
- Extended backend and live browser gates to cover history/sidebar behavior,
  safe Q&A, missing-information refusal, context boundary behavior, and
  cross-user Q&A denial
- The Postgres gate starts or reuses Docker Compose Postgres, creates a clean
  `lexi_e2e_8011` database, applies Alembic migrations before API startup, and
  passes the same lease-verification browser path with eager Celery
- Extended the live browser gate to assert cross-user result, job-status, and
  delete attempts return `404`
- Updated the results UI to prefer the backend grounded summary payload and
  extended the live browser gate to assert it appears
- Added low-confidence fallback summaries so Lexi avoids model inference when
  extracted text quality is weak
- Added an Ollama-compatible LLM provider adapter and network-free tests for
  provider selection/request construction
- Added summary tests for missing document facts so absent lease details are not
  invented
- Documented the Phase 2 product decision to make Lexi a document-centered conversation workspace, not a generic legal chatbot
- Added planning guidance for document history/sidebar, scoped Q&A, optional user context, and unsupported-document guardrails
- Consolidated technical documentation: `design.md` is now the canonical system design, including architecture plus data/auth strategy
- Rewrote `requirements.md` as project-wide requirements covering MVP, RAG/Q&A, RiskSense, integrations, public-beta auth, and future expansion
- Docker stack runs reliably (API, worker, PostgreSQL, Redis, MinIO, Qdrant)
- Alembic migrations apply automatically on API startup
- Backend API gate passes with isolated temp SQLite
- Live browser lease-verification gate passes against a live FastAPI test server, eager worker, and isolated temp SQLite
- Python setup prefers `mamba`, falls back to `conda`
- Contributor onboarding scripts added (`scripts/onboarding/`)

**April 2026**
- Code reorganization: `backend/core/`, `backend/ml/`, `backend/services/`
- API consolidated under `backend/api/v1/`
- Repository layout cleanup (moved operational files to `backend/`)
- Frontend `.gitignore` typo fixed (`.vinext/` → `.next/`)

---

## 📚 Documentation Status

**Complete**
- Vision and mission (`README.md`)
- Product roadmap (`docs/product/roadmap.md`)
- Technical system design (`docs/technical/design.md`)
- Project-wide requirements (`docs/technical/requirements.md`)
- Integration contract (`docs/technical/contract.md`)
- Active technical task board (`docs/technical/tasks.md`)
- Setup guide (`docs/technical/SETUP.md`)
- UI implementation guide (`docs/product/styles.md`)
- User testing plan (`docs/product/user-testing.md`)
- Contributing guide (`CONTRIBUTING.md`)

## 🔗 Alignment with Roadmap

This changelog reflects completion of:
- ✅ **Phase 0:** Foundations (architecture, documentation, safety boundaries)
- ✅ **Phase 1:** Backend MVP (document processing pipeline)
- ✅ **Phase 1.5:** Frontend MVP (user interface)
- ✅ **Phase 2:** RAG Pipeline first slice (grounded summaries, guarded document Q&A, source excerpts)
- ✅ **Phase 3:** RiskSense first MVP slice (source-grounded rule-based risk signals and confidence rollups)

Next phases align with roadmap priorities:
- Output reliability and usefulness pass
- Real-lease RiskSense evaluation
- Observed user testing and public-beta hardening
- Future analytics, multi-document support, language access, and community integrations

See [roadmap.md](../product/roadmap.md) for full phased plan.

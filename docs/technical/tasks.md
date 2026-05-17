# Lexi Technical Task Board

This is the active engineering task board. It replaces the older Phase 1 implementation checklist and is now aligned with the canonical project docs: `design.md`, `requirements.md`, and `CHANGELOG.md`.

Use this file for what to build next. Use `docs/product/roadmap.md` for why it matters.

## Current Position

Lexi is a technical MVP for Ontario residential lease verification.

Completed foundations:

- Phase 0 product and safety foundation
- Phase 1 backend document lifecycle foundation
- Phase 1.5 UI MVP
- Fast backend API E2E gate
- Live browser lease-verification gate against a live FastAPI test server
- Postgres-backed E2E release gate
- Grounded LLM summaries with deterministic tests and low-confidence fallback
- Early RAG scaffolding
- Unsupported-document guardrails for `unknown` classification
- First RiskSense MVP slice

Current strategic order:

1. Improve the reliability and usefulness of Lexi’s summaries, Q&A, source excerpts, and RiskSense output
2. Evaluate output against saved screenshots, synthetic samples, and real Ontario lease examples
3. Run broader observed user testing after the output-quality pass
4. Keep extraction edge-case unit tests tracked, but intentionally deferred for now

## Task Status Key

- `[x]` Done
- `[ ]` Next / not done
- `[~]` Started or partial
- `[>]` Deferred intentionally

## Done: Product Proof Gates

- [x] Backend API gate proves register/login -> upload -> consent -> eager worker -> results -> delete -> post-delete 404s.
- [x] Live browser gate proves the same lease flow through the Next.js UI against a live FastAPI test server.
- [x] SQLite is documented as test-only; Postgres remains the product database.
- [x] Custom JWT auth is documented as private-MVP only.
- [x] Supabase Auth is documented as the recommended public-beta option unless custom auth is deliberately hardened.

## Done: Postgres-Backed E2E Gate

Goal: prove the current lease verification path against Docker Postgres and Alembic migrations, not just temp SQLite.

- [x] Add a Postgres E2E test mode that starts or reuses Docker Postgres.
- [x] Apply Alembic migrations before the test server starts.
- [x] Run the same browser lease-verification path against Postgres.
- [x] Keep Celery eager mode for determinism unless testing the full worker queue is the explicit goal.
- [x] Keep uploads isolated in a temp directory.
- [x] Ensure cleanup removes test users, documents, job statuses, metadata, summaries, clauses, consent records, and temp files.
- [x] Add a dedicated command: `cd frontend && npm run test:e2e-lease:postgres`.
- [x] Document when to run it: CI, release cuts, and before public-beta milestones.

Verification note, 2026-05-16:

- Existing live browser gate passed with the new user-scoping assertions.
- Postgres gate passed after Docker was available; it started/reused Docker Postgres,
  applied Alembic migrations, and ran the live browser lease-verification flow.

Acceptance:

- The existing live browser gate still passes.
- The new Postgres gate passes from a clean Docker database.
- Post-delete results and job status return `404`.
- User scoping is preserved.

## Done: Grounded LLM Summaries

Goal: make Lexi useful in plain language without letting the model invent facts.

- [x] Add an LLM provider interface with a fake/test provider and at least one real provider adapter.
- [x] Keep provider configuration in environment variables.
- [x] Add a summary payload shape to schemas.
- [x] Generate summaries only from extracted text or retrieved clause context.
- [x] Include uncertainty/fallback behavior when extraction confidence is low.
- [x] Add tests for “not in document” behavior.
- [x] Extend the backend API gate to assert summary presence with the fake provider.
- [x] Extend the live browser gate to verify the summary appears without weakening the current lifecycle assertions.

Acceptance:

- Summary text is grounded in the uploaded lease.
- No legal-advice language is introduced.
- Tests can run without paid/network LLM calls.

Verification note, 2026-05-16:

- Added a conservative low-extraction-confidence fallback summary.
- Added an Ollama-compatible provider adapter while keeping tests network-free.
- Added summary tests for missing facts, low-confidence fallback, and provider selection.

## Done: Document Workspace and Limited Q&A

Goal: turn the linear MVP flow into a document-centered conversation workspace
and activate the existing RAG scaffolding safely.

- [x] Clause chunking exists.
- [~] Qdrant adapter exists.
- [x] `/documents/{id}/ask` endpoint exists.
- [x] Add `GET /api/v1/documents` for a user-scoped document history/sidebar
      that returns safe metadata/status, not extracted document text.
- [x] Decide whether Phase 2 stores Q&A messages or uses one live conversation
      per processed document until persistence is needed.
- [x] Rework the frontend into a document-centered workspace:
      sidebar/history, active document header, upload/consent states, summary,
      source excerpts, and chat.
- [x] Keep the active document visible while asking and answering questions.
- [x] Add optional user situation/context input that is clearly separated from
      extracted document facts.
- [x] Add deterministic test doubles for embeddings/vector retrieval.
- [x] Add a document-scoped Q&A UI.
- [x] Require answers to cite or quote retrieved text.
- [x] Add “I don’t know from this document” behavior.
- [x] Add hallucination boundary tests.
- [x] Extend the live browser gate to cover one safe document-scoped Q&A interaction.

Acceptance:

- Users can return to their own processed documents from the sidebar/history.
- The primary object in the UI is the active document, not a generic chat.
- Questions are answered only from the uploaded document.
- Missing information produces a safe refusal/uncertainty response.
- User-provided context does not override source document text.
- Q&A remains clearly informational, not legal advice.

Verification note, 2026-05-16:

- Added safe user-scoped document history through `GET /api/v1/documents`.
- Chose non-persisted in-memory Q&A threads for the current UI; persistence is
  deferred until the answer behavior is beta-safe.
- Added deterministic in-memory vector retrieval and hashed embeddings for tests
  and live browser gates.
- Reworked the home workflow into a document workspace with sidebar/history,
  active document header, source excerpts, and document-scoped chat.
- Added extractive Q&A answers with citations, missing-information behavior, and
  a clear separation between optional user context and document evidence.
- Extended backend and live browser gates to cover history, Q&A citations,
  missing-information refusal, context-not-overriding-source behavior, and
  cross-user Q&A denial.

## Done: Unsupported-Document Guardrails

Goal: make accidental or unsupported uploads safe before chat becomes a beta
surface.

- [x] Add or harden backend behavior for `unknown` documents so they do not
      receive legal-style summaries, RiskSense outputs, or broad Q&A.
- [x] Add a clear frontend unsupported state for `unknown` classification with
      confidence, delete, and upload-another actions.
- [x] Add tests with supported file formats containing non-lease/random content.
- [x] Ensure wording says "unsupported by Lexi" rather than claiming the file is
      definitively non-legal.

Verification note, 2026-05-16:

- Unknown classifications now skip clause extraction, metadata extraction,
  retrieval indexing, and grounded summary generation.
- Summary generation is also guarded at the service boundary so unsupported
  documents cannot receive legal-style summaries through a direct service call.
- Unsupported documents complete successfully with `document_type: "unknown"`,
  no clauses, no summary, and Q&A unavailable with "unsupported by Lexi"
  recovery wording.
- The frontend shows a calm unsupported state with confidence, delete, and
  upload-another actions, without showing legal chat or summary affordances.
- Added backend DOCX/PDF random-content regression coverage and a live browser
  unsupported-document path.

Acceptance:

- Random supported-format files complete in a safe unsupported state.
- Lexi does not invite legal chat for unsupported documents.
- Users know what happened and how to recover without seeing internal errors.

## Done: Auth Public-Beta Decision

Goal: avoid sleepwalking custom auth into public beta.

- [x] Add `AUTH_PROVIDER=custom` and Supabase config placeholders.
- [x] Record the decision in the canonical task board and auth design docs:
      Supabase Auth is the public-beta path; custom auth remains private-MVP
      and local-E2E only.
- [x] If Supabase is chosen:
  - [x] Verify Supabase JWTs in FastAPI.
  - [x] Map Supabase subject IDs to Lexi document ownership.
  - [x] Replace frontend custom login/register with Supabase client flows.
  - [x] Keep FastAPI as the document-processing authority.
- [>] If custom auth is kept:
  - [>] Add email verification.
  - [>] Add password reset.
  - [>] Add refresh/session handling.
  - [>] Add rate limiting and brute-force protection.
  - [>] Add session revocation.
  - [>] Move away from localStorage-only token storage for public users.

Acceptance:

- Public-beta auth path is chosen before external onboarding.
- Private MVP remains functional with custom auth for local work and E2E gates.
- Custom-auth hardening is intentionally deferred unless the Supabase decision
  is reversed.

Verification note, 2026-05-16:

- Chose Supabase Auth for public beta and recorded the decision inline in the
  technical task board and auth design docs.
- Added provider-aware backend auth. `AUTH_PROVIDER=custom` preserves the
  private MVP flow; `AUTH_PROVIDER=supabase` disables custom register/login,
  verifies Supabase JWTs through JWKS, and maps Supabase `sub` values to Lexi
  document ownership.
- Custom auth hardening is not part of the public-beta path unless this
  decision is reversed.

Verification note, 2026-05-17:

- Added provider-aware frontend auth. `NEXT_PUBLIC_AUTH_PROVIDER=custom`
  preserves the private-MVP login/register flow and E2E gates; setting
  `NEXT_PUBLIC_AUTH_PROVIDER=supabase` uses Supabase client sign-up, sign-in,
  password reset, session refresh, and sign-out flows.
- The frontend sends the active bearer token to FastAPI for document upload,
  history, consent, results, delete, job status, and Q&A. FastAPI remains the
  document-processing and authorization authority.
- Fixed the live Docker upload failure that caused processed documents to show
  `failed`: API and worker containers now share the configured upload temp
  volume.
- Added a graceful failed-processing workspace state so users see recovery
  actions instead of a stale "Analyzing your document..." composer.

## Done: RiskSense MVP

Goal: add risk intelligence after lifecycle, summary, and retrieval behavior are trustworthy.

- [x] Define the first risk output schema: severity, confidence, reason, source clause.
- [x] Implement a rule-based first pass for lease risks.
- [x] Add confidence rollups across extraction, classification, metadata, and risk signals.
- [x] Add “top risks” summary with calm, non-alarmist language.
- [x] Add UI section for RiskSense without paywalling basic understanding.
- [x] Add tests that prevent legality claims and outcome prediction.

Verification note, 2026-05-17:

- Added persisted, source-grounded `risk_signals` with severity, confidence,
  reason, rule ID, and source clause linkage.
- Added deterministic rule-based RiskSense generation for rent/payment timing,
  extra charge language, landlord entry, tenant maintenance responsibility,
  utilities, termination notice, and subletting/assignment approval.
- Added results payloads with `risk_sense.top_risks_summary`,
  `risk_sense.confidence_rollup`, and source-grounded risk signals.
- Added the RiskSense section to the document workspace with calm copy,
  source excerpts, confidence rollups, and smooth entry motion.
- Added backend and browser test assertions for supported leases, unsupported
  documents, source grounding, and generated-language safety boundaries.
- Frontend production build passed in the current shell.
- Backend runtime tests were blocked in the current shell because the project
  Python dependencies were not active (`sqlalchemy` and `python-docx` missing).

Acceptance:

- Supported Ontario lease results include basic RiskSense attention signals.
- Unsupported `unknown` documents do not receive RiskSense output.
- Every risk signal is attached to source clause text.
- Generated risk titles, reasons, and summaries avoid legality claims and
  outcome prediction.
- Basic understanding and basic risk flags remain available without a paywall.

## Done: User Testing Readiness Prep

Goal: validate usefulness with real people, not just passing tests.

- [x] Run the full backend API gate in the project Python environment.
- [x] Run the live browser lease-verification gate with RiskSense assertions.
- [x] Prepare 3-5 sample Ontario lease scenarios.
- [x] Confirm the user testing playbook and trackers are current.
- [x] Add a private-beta testing checklist.
- [x] Capture a synthetic review pass against saved sample outputs.
- [>] Run 5-10 external observed sessions after the output-quality pass.
- [>] Capture top 3 external UX issues and top 3 external trust/safety issues.

Acceptance:

- 80%+ complete upload successfully.
- 90%+ understand consent.
- 70%+ find results helpful.
- Findings feed the next sprint.

Verification note, 2026-05-17:

- Fixed the project-environment backend gate hang by keeping FastAPI auth
  dependencies on the async dependency path while preserving direct sync
  security helpers for unit tests. The hang was caused by synchronous
  dependencies taking the local AnyIO threadpool path before custom auth
  endpoints could respond.
- Backend API gate passed in the `lexi` Python environment:
  `17 passed, 2 warnings`.
- Live browser lease-verification gate passed with RiskSense assertions:
  `2 passed`.
- Simplified the user-facing consent path so upload is temporary intake and the
  post-upload consent panel is the single analysis permission step.
- Added a compact results readiness strip for document type, extraction
  confidence, classification confidence, and source clause count.
- Added `docs/product/testing-kit/sample-lease-scenarios.md` with 5 Ontario
  lease scenarios.
- Added `docs/product/testing-kit/private-beta-checklist.md` and refreshed the
  playbook, recruitment tracker, participant log, and analysis template for
  upload, consent, helpfulness, Q&A, RiskSense, UX, and trust/safety metrics.

Synthetic review note, 2026-05-17:

- A synthetic review pass was completed against diverse sample images in
  `docs/media/samples` and the saved product screenshots.
- Top UX issues: status chips used overly strong semantic colors; the
  unsupported-document state looked like a warning because of the yellow
  treatment; the account/workspace sidebar did not consistently fill the
  viewport and needed more breathing room before the document list or empty
  state.
- Top trust/safety issues: a green "complete" state over-signaled certainty on
  low-confidence extractions; unsupported uploads needed calm recovery framing
  instead of alert styling; destructive actions looked too severe for a
  reading-companion interface.

## Next: Output Reliability and Value Pass

Goal: make Lexi’s output helpful enough to justify the product flow before
adding more extraction edge-case unit coverage.

- [ ] Review saved screenshots and sample outputs for vague, thin, repetitive,
      or overconfident language.
- [ ] Improve summary shaping so Lexi names the most important document facts,
      missing information, and user-facing next questions.
- [ ] Improve source excerpt selection so citations feel relevant, not merely
      present.
- [ ] Tighten document Q&A responses around "answer from the document" behavior,
      especially when the answer is absent or only partly supported.
- [ ] Tune RiskSense severity, confidence, and reason copy against sample and
      real Ontario lease examples.
- [ ] Save before/after examples or notes so the next changelog entry can
      explain what became more useful.
- [>] Expand extraction edge-case unit tests after the output-quality pass
      clarifies the target behavior.

Acceptance:

- Summaries identify concrete document facts instead of generic reassurance.
- RiskSense flags point to understandable source text and avoid legal claims.
- Q&A says when the document does not answer instead of filling gaps.
- Low-confidence or unsupported outputs look calm and appropriately limited.

## Backlog: Phase 1 Hardening

These are still useful, but they should not block the output-reliability pass
unless they touch a failing product proof.

- [>] Unit tests for PDF extraction edge cases.
- [>] Unit tests for DOCX extraction edge cases.
- [>] Unit tests for OCR low-confidence behavior.
- [>] Unit tests for clause boundary and type tagging.
- [>] Unit tests for metadata extraction variants.
- [ ] Tests for persistent storage mode with S3/MinIO.
- [ ] Tests for consent declined -> immediate deletion.
- [ ] Tests for cross-user access denial.
- [ ] Rate limiting and upload abuse protections.
- [ ] Monitoring/logging review for private beta.

## Documentation Hygiene

- [x] `design.md` is the canonical system design, including architecture plus data/auth strategy.
- [x] `docs/README.md`, root `README.md`, and `SETUP.md` point to the consolidated docs.
- [x] `CHANGELOG.md` records the documentation consolidation.

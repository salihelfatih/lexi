# Lexi Project Requirements

> Living project-wide requirements for Lexi.
>
> Last updated: May 16, 2026

## Purpose

This document defines what Lexi must do across the whole product, not just the
first upload-processing phase. It is the acceptance baseline for engineering,
product, safety, and integration decisions.

Use [design.md](design.md) for system design and architecture, [tasks.md](tasks.md)
for active work, and [../product/roadmap.md](../product/roadmap.md) for phased
delivery order.

## Status Labels

- **Current**: implemented or partially implemented in the active MVP
- **Next**: near-term work needed before private/public beta readiness
- **Planned**: product requirement accepted, implementation not started
- **Invariant**: must remain true in every phase

## Glossary

- **User**: A person using Lexi to understand an uploaded document.
- **Document**: A file uploaded by a user, currently PDF, DOCX, JPEG, or PNG.
- **Processing Consent**: Explicit permission to analyze an uploaded document.
- **Storage Consent**: Optional permission to persist a document beyond
  processing.
- **Ephemeral Mode**: Default mode where files and derived data are temporary and
  removable.
- **Persistent Mode**: Storage mode selected only after storage consent.
- **Grounding**: The requirement that outputs use extracted document text,
  clauses, or retrieved chunks as source evidence.
- **RAG**: Retrieval-augmented generation for document-scoped answers.
- **RiskSense**: Lexi risk-intelligence layer; first MVP slice is rule-based and source-grounded.
- **Product Runtime Database**: PostgreSQL.
- **Fast Test Database**: Throwaway SQLite used only for isolated automated
  tests.

## Requirement 1: Legal Information Boundary

**Status:** Invariant

**User Story:** As a user, I want Lexi to help me understand legal documents
without pretending to be my lawyer.

### Acceptance Criteria

1. Lexi MUST describe itself as legal information, not legal advice.
2. Lexi MUST NOT declare whether a clause is legal or illegal.
3. Lexi MUST NOT predict legal outcomes.
4. Lexi MUST NOT tell users what decision to make.
5. Lexi MUST clearly communicate uncertainty when confidence is low or context is
   missing.
6. Lexi MUST encourage users to seek qualified legal or clinic support when
   appropriate.
7. All LLM and RiskSense outputs MUST stay within this boundary.

## Requirement 2: User Accounts and Ownership

**Status:** Current

**User Story:** As a user, I want my documents tied to my own account so other
users cannot access them.

### Acceptance Criteria

1. Lexi MUST support user registration for the private MVP.
2. Lexi MUST support login and authenticated API calls.
3. Lexi MUST scope every document read, result read, job read, and delete action
   to the authenticated owner.
4. Lexi MUST reject access to another user's documents.
5. Lexi MUST keep custom JWT auth acceptable only for private MVP unless it is
   deliberately hardened.
6. Lexi MUST use Supabase Auth for public beta unless this decision is reversed
   in the active technical task board and auth design docs.
7. With Supabase Auth, FastAPI MUST verify Supabase JWTs and keep document
   authorization server-side.
8. If custom auth is ever kept for public users, Lexi MUST add email
   verification, password reset, refresh/session handling, rate limiting,
   revocation, and safer browser token storage before public beta.

## Requirement 3: Consent and Privacy Control

**Status:** Current

**User Story:** As a user, I want to choose whether Lexi processes or stores my
private documents.

### Acceptance Criteria

1. Lexi MUST request processing consent before analysis starts.
2. Lexi MUST request storage consent separately from processing consent.
3. Lexi MUST delete the uploaded document immediately when processing consent is
   declined.
4. Lexi MUST default to ephemeral mode when storage consent is not granted.
5. Lexi MUST record consent decisions and timestamps.
6. Lexi MUST explain that user documents are not used for model training without
   explicit opt-in.
7. Lexi MUST keep consent visible and understandable in the UI.
8. Integrations MUST NOT silently send documents to Lexi without explicit user
   action or explicit granted access.

## Requirement 4: Secure Document Upload

**Status:** Current

**User Story:** As a user, I want to upload common lease formats safely and get
clear feedback if something fails.

### Acceptance Criteria

1. Lexi MUST accept PDF files.
2. Lexi MUST accept DOCX files.
3. Lexi MUST accept JPEG files.
4. Lexi MUST accept PNG files.
5. Lexi MUST reject files above the configured maximum size.
6. Lexi MUST reject unsupported formats with a user-friendly message.
7. Lexi MUST support click-to-browse file selection in the UI.
8. Lexi SHOULD support drag-and-drop file selection.
9. Lexi MUST avoid returning stack traces or internal errors to users.
10. Lexi SHOULD preserve enough upload metadata for debugging without logging
    document content or PII.

## Requirement 5: Text Extraction and OCR

**Status:** Current for MVP; Planned for deeper hardening

**User Story:** As a user, I want Lexi to read my document whether it is digital,
scanned, or photographed.

### Acceptance Criteria

1. Lexi MUST extract selectable text from native PDFs.
2. Lexi MUST extract text from DOCX files.
3. Lexi MUST perform OCR for scanned documents and image uploads.
4. Lexi MUST return extraction confidence.
5. Lexi MUST warn or fail safely when extraction quality is too low.
6. Lexi MUST preserve enough structure for clause parsing and grounding.
7. Lexi SHOULD handle paragraph boundaries, headings, numbered clauses, lists,
   and tables as implementation matures.
8. Lexi SHOULD detect or tolerate multi-column layouts.
9. Lexi MUST never invent text that was not extracted.

## Requirement 6: Document Classification

**Status:** Current for Ontario leases; Planned for additional document classes

**User Story:** As a user, I want Lexi to tell me whether it understands the type
of document I uploaded.

### Acceptance Criteria

1. Lexi MUST classify uploaded documents after text extraction.
2. Current MVP MUST support `ontario_residential_lease`.
3. Current MVP MUST classify unsupported or uncertain documents as `unknown`.
4. Lexi MUST expose classification confidence.
5. Lexi MUST avoid confident claims when classification confidence is low.
6. Lexi MUST describe `unknown` documents as unsupported by Lexi, not as a
   definitive finding that the file is or is not legal.
7. Lexi MUST NOT show RiskSense outputs for `unknown` documents.
8. Lexi MUST NOT offer broad legal Q&A for `unknown` documents.
9. Lexi SHOULD offer clear next actions for `unknown` documents, including
   delete and upload another file.
10. Lexi SHOULD expand to additional document types only when each type has its
   own safe extraction, explanation, and risk requirements.

## Requirement 7: Clause and Structure Extraction

**Status:** Current for MVP lease clauses; Next for hardening

**User Story:** As a user, I want Lexi to break my document into meaningful
sections so I can inspect the source text.

### Acceptance Criteria

1. Lexi MUST extract clauses or sections for supported document types.
2. Lexi MUST preserve original clause text for grounding.
3. Lexi MUST preserve clause ordering.
4. Lexi MUST tag common lease clause types such as termination, fees, access,
   maintenance, utilities, pets, subletting, and other.
5. Lexi MUST use fallback boundaries when numbering is ambiguous.
6. Lexi SHOULD support nested numbering and mixed numbering schemes.
7. Lexi SHOULD expose clause confidence as the parser matures.
8. Clause extraction failures MUST fail safely and explain that the structure
   could not be parsed.

## Requirement 8: Metadata Extraction

**Status:** Current for lease MVP

**User Story:** As a user, I want key details pulled out so I can quickly check
whether Lexi understood the document.

### Acceptance Criteria

1. Lexi MUST extract lease start date when present.
2. Lexi MUST extract lease end date when present.
3. Lexi MUST extract tenant names when present.
4. Lexi MUST extract landlord names when present.
5. Lexi MUST extract rental property address when present.
6. Lexi MUST extract monthly rent when present.
7. Missing values MUST be shown as not found rather than fabricated.
8. Ambiguous values SHOULD include lower confidence or warnings.
9. Metadata MUST be returned in structured API responses.

## Requirement 9: Results and Plain-English Summary

**Status:** Current for structured results, backend summaries, MVP UI display,
low-confidence fallback, deterministic tests, and a local real-provider adapter

**User Story:** As a user, I want a clear explanation of what Lexi found, grounded
in my document.

### Acceptance Criteria

1. Lexi MUST return classification, metadata, clauses, extraction confidence, and
   total clause count after processing.
2. Lexi MUST generate summaries only from extracted text, extracted clauses, or
   retrieved source chunks.
3. Lexi MUST support deterministic summary generation in automated tests without
   network or paid LLM calls.
4. Lexi SHOULD display the backend grounded summary in the UI when available.
5. Lexi MUST avoid legal advice language in summaries.
6. Lexi MUST include uncertainty or fallback behavior when source quality is low.
7. Lexi SHOULD expose summary source information such as source count and
   grounding type.

## Requirement 10: Document-Scoped Q&A

**Status:** Initial limited implementation complete; broader natural-language Q&A remains future work

**User Story:** As a user, I want to ask questions about my uploaded document and
get answers based only on that document.

### Acceptance Criteria

1. Lexi MUST retrieve context only from the user's selected document.
2. Lexi MUST answer using only retrieved document chunks.
3. Lexi MUST say when the answer is not present in the document.
4. Lexi MUST cite, quote, or otherwise expose source text for answers.
5. Lexi MUST prevent cross-user retrieval.
6. Lexi MUST provide deterministic test doubles for embeddings and retrieval.
7. Lexi MUST include hallucination boundary tests before Q&A is treated as beta
   ready.
8. Lexi MUST keep Q&A informational, not advisory.
9. Lexi MUST make the active document clear in the Q&A interface.
10. Lexi MUST NOT present document Q&A as a general legal chatbot.
11. Lexi SHOULD support a document-centered chat UI after upload, consent, and
    successful processing.
12. User-provided situation context MAY be included, but it MUST be separated
    from extracted document facts and must not override source text.
13. Lexi SHOULD preserve or reconstruct useful document conversation history
    for user navigation, subject to consent and deletion rules.

## Requirement 11: RiskSense

**Status:** Current for first rule-based MVP slice; planned for advanced analytics

**User Story:** As a user, I want Lexi to highlight clauses that may deserve
attention without scaring me or pretending to judge legality.

### Acceptance Criteria

1. RiskSense MUST attach every risk signal to source document text.
2. RiskSense MUST include severity.
3. RiskSense MUST include confidence.
4. RiskSense MUST include a reason in plain language.
5. RiskSense MUST avoid legality claims.
6. RiskSense MUST avoid legal outcome predictions.
7. RiskSense MUST use calm, non-alarmist language.
8. RiskSense SHOULD begin with a rule-based first slice before adding more
   complex ML/LLM behavior.
9. Premium risk analytics MUST deepen understanding without paywalling basic
   legal understanding.

## Requirement 12: Data Storage and Lifecycle

**Status:** Current for core lifecycle and Postgres release gate

**User Story:** As a user, I want my data stored only when I allow it and deleted
when I ask.

### Acceptance Criteria

1. Lexi MUST use PostgreSQL for product runtime.
2. Lexi MUST use SQLite only for fast isolated tests.
3. Lexi MUST use Alembic migrations for product schema changes.
4. Lexi MUST keep uploaded files temporary before consent and in ephemeral mode.
5. Lexi MUST use S3-compatible storage for persistent document storage.
6. Lexi MUST encrypt persistent documents at rest.
7. Lexi MUST support one-click document deletion.
8. After deletion, document results MUST return `404`.
9. After deletion, job status MUST return `404`.
10. Deletion MUST remove dependent metadata, summaries, clauses, risk signals,
    consent records, job statuses, object-storage content when present, and temp files.

## Requirement 13: Security, Logging, and Abuse Prevention

**Status:** Partial; Next before public beta

**User Story:** As a user, I want Lexi to protect sensitive documents throughout
processing.

### Acceptance Criteria

1. Lexi MUST transmit production traffic over HTTPS.
2. Lexi MUST never log document text.
3. Lexi MUST never log sensitive personal details from uploaded documents.
4. Lexi MUST log operational identifiers and error codes sufficient for
   debugging.
5. Lexi MUST isolate document processing from unrelated users' data.
6. Lexi MUST use strong secrets in production.
7. Lexi MUST add rate limiting and upload abuse protections before public beta.
8. Lexi SHOULD add monitoring and alerting before external onboarding.
9. Lexi SHOULD document backup and restore procedures before production use.

## Requirement 14: Product Access Model

**Status:** Product-defined; implementation phased

**User Story:** As a user, I want basic legal understanding to remain useful even
if premium analytics are added later.

### Acceptance Criteria

1. Free Lexi MUST include useful basic document understanding.
2. Free Lexi SHOULD include upload, extraction, summary, basic clauses, key
   metadata, basic risk flags, and limited document-scoped Q&A.
3. Premium Lexi MAY include advanced risk scoring, severity, confidence rollups,
   financial estimates, comparison, forecasting, pattern detection, and document
   history.
4. Premium Lexi MUST remain legal information, not legal advice.
5. Basic protection and comprehension MUST NOT be paywalled.
6. Organization plans MUST use anonymized, consent-aware, privacy-preserving
   analytics.

## Requirement 15: Integrations

**Status:** Planned and governed by contract

**User Story:** As a partner app, I want Lexi to add document understanding
without taking over my workflow or violating user trust.

### Acceptance Criteria

1. Lexi MUST be usable as a standalone flow.
2. Lexi SHOULD support embedded integrations in apps such as RiseUp and fLOKr.
3. Lexi SHOULD support API-based integrations for analysis, summaries, flags,
   questions, risk outputs, and analytics.
4. Integrations MUST require explicit user action or explicit granted access.
5. Integrations MUST receive structured, explainable, source-grounded outputs.
6. Host applications MUST retain ownership of their user workflow.
7. Organization analytics MUST NOT expose individual user documents.

## Requirement 16: User Experience and Accessibility

**Status:** Current MVP; Next for user testing

**User Story:** As a non-technical user, I want Lexi to feel calm, clear, and
usable on common devices.

### Acceptance Criteria

1. Lexi MUST provide a clear upload -> consent -> processing -> results ->
   deletion flow.
2. Lexi MUST show processing status.
3. Lexi MUST make consent and storage choices understandable.
4. Lexi MUST keep legal-advice boundaries visible.
5. Lexi SHOULD be mobile-friendly.
6. Lexi SHOULD support export or print-friendly output.
7. Lexi SHOULD use plain language and avoid unnecessary legal jargon.
8. Lexi SHOULD keep the Phase 2 UI organized around a document-centered
   conversation workspace with a user-scoped document history/sidebar.
9. Lexi SHOULD keep basic document navigation available as core usability; paid
   document monitoring may add deeper analytics but must not block basic access
   to a user's own processed documents.
10. Lexi SHOULD use motion only to clarify state changes, not to make the
    product feel like a generic AI assistant.
11. Lexi SHOULD validate usability with renters, students, newcomers, and
   community/legal support partners.

## Requirement 17: Testing and Release Gates

**Status:** Current for SQLite gates and Postgres-backed release gate

**User Story:** As a maintainer, I want confidence that the core lifecycle works
before shipping changes.

### Acceptance Criteria

1. Lexi MUST maintain a backend API gate for register/login, upload, consent,
   eager worker processing, results, deletion, and post-delete `404`s.
2. Lexi MUST maintain a live browser gate for the same lifecycle through the UI.
3. Fast gates MAY use isolated SQLite for deterministic local feedback.
4. Lexi MUST maintain a Postgres-backed E2E gate before public beta.
5. The Postgres gate MUST run against Docker Postgres and Alembic migrations.
6. The Postgres gate MUST preserve user scoping and cleanup assertions.
7. LLM summary tests MUST run without paid/network LLM calls.
8. Q&A and RiskSense MUST add hallucination/safety boundary tests before release.
9. CI SHOULD run fast gates on every relevant change and the Postgres gate before
   releases.

## Requirement 18: Future Document Classes and Language Access

**Status:** Planned

**User Story:** As Lexi expands, I want new document types and languages to be as
safe and clear as the lease MVP.

### Acceptance Criteria

1. Lexi MAY expand beyond Ontario leases only with document-type-specific
   extraction, summary, Q&A, and risk requirements.
2. Lexi MAY support employment contracts, offer letters, school documents,
   government notices, and other legal documents in later phases.
3. Lexi SHOULD support multilingual explanations when translation safety and
   confidence are designed.
4. Translations MUST preserve uncertainty and legal-information boundaries.
5. Lexi MUST clearly signal translation limits.
6. New document types and languages MUST not weaken privacy, consent, grounding,
   or safety requirements.

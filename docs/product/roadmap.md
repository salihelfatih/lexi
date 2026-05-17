# 🛣️ Lexi — Product & Engineering Roadmap

This roadmap outlines the phased development of **Lexi Intelligence System**.

Lexi prioritizes **trust, safety, and grounded understanding** over speed or hype.
Features ship only when they reduce confusion and harm, not when they merely impress.

---

## Guiding Principles

- Start narrow, earn trust, then expand
- Ground every explanation in source documents
- Prefer conservative behavior over confident mistakes
- Keep basic legal understanding free and useful
- Use premium analytics to deepen risk insight, not to gate protection
- Ship working systems before ambitious claims
- Grow capabilities without increasing legal or ethical risk

---

## Product Access Model

### Free Lexi
**Positioning:** “Understand what you’re signing.”

Free Lexi should include:
- Document upload
- OCR and text extraction
- Plain-English summaries
- Basic clause extraction
- Key dates and metadata
- Basic risk flags
- Limited document-scoped Q&A

Basic legal understanding must not be paywalled.

### Premium Lexi Risk Intelligence
**Positioning:** “Understand the risks before they become expensive.”

Premium adds deeper risk analytics:
- Advanced risk scoring
- Severity levels for flagged clauses
- Confidence scoring across OCR, classification, extraction, and LLM outputs
- Financial impact estimation
- Lease comparison
- Renewal and penalty forecasting
- Pattern detection across documents
- Prioritized “top risks” summaries
- AI-generated negotiation or clarification questions
- Document history and monitoring

Premium remains legal information, not legal advice.

### Organization Plans
Lexi may support tenant unions, student associations, nonprofits, and legal clinics through:
- Aggregated anonymized risk trends
- Bulk document analysis
- Pattern detection across leases or contracts
- Dashboards for recurring exploitative clauses
- Exportable reports for advocacy, education, or clinic workflows

Organization insights must be anonymized, consent-aware, and privacy-preserving.

---

## Phase 0 — Foundations (Design & Alignment)

**Status:** Complete

**Goals**
- Lock product scope and safety boundaries
- Establish architecture for hybrid AI (ML + LLM + RAG)
- Define non-negotiable guardrails

**Key Deliverables**
- Project README (scope, safety, tech stack)
- Vision & mission document
- AI architecture design (OCR → ML → RAG → LLM)
- Legal and ethical risk assessment
- Document schemas and API contracts

**Why this matters**
This phase prevents downstream rework and legal risk.
Lexi’s guardrails are designed before features, not after.

---

## Phase 1 — MVP: Lease Understanding (Trust First)

**Status:** Backend foundation complete; end-to-end verification gate passing

**Scope**
- Residential leases and student housing agreements
- English language
- Conservative, information-only behavior

**Core Features**
- Secure document upload with explicit consent
- OCR and text extraction (PDFs, scans, photos)
- Document classification (lease vs unknown)
- Plain-English summary grounded in clauses
- Key dates and deadlines extraction
- Initial risk and attention flags
- Report generation and export

**ML & AI**
- Hugging Face transformer for document classification
- Rule-based clause extraction
- LLM-based summarization with clause citations
- No open-ended Q&A yet

**Success Criteria**
- Users understand documents better than before
- Lexi never invents facts
- Explanations are calm, accurate, and readable

---

## Phase 1.5 — User Interface (Accessibility First)

**Status:** MVP complete; live browser verification gate passing

**Scope**
- React-based web application
- Mobile-responsive design
- Accessible to non-technical users

**Core Features**
- Drag-and-drop document upload
- Visual consent flow with clear privacy notices
- Real-time processing status with progress indicators
- Results page with document summary and clause breakdown
- Export to PDF functionality
- One-click document deletion

**Design Principles**
- Calm and clear (no overwhelming complexity)
- Supportive, not authoritative
- Privacy-first (make consent obvious)
- Honest about uncertainty (show confidence scores)
- Mobile-friendly and accessible

**Success Criteria**
- Target users can upload and understand documents without help
- 90%+ understand consent flow
- Works smoothly on mobile devices
- Enables real user testing and feedback
- Required for RiseUp/fLOKr integration

**Why This Phase**
Without a UI, Lexi remains inaccessible to its target audience (students, renters, newcomers). The backend is functional, but users need a friendly interface to benefit from Lexi's capabilities.

See `docs/product/styles.md` (UI Implementation Guide) for detailed implementation plan.

---

## Phase 2 — RAG-Powered Understanding (Grounded Intelligence)

**Status:** Early scaffolding exists; deterministic backend summary path, low-confidence fallback, local real-provider adapter, document workspace/sidebar, source excerpts, limited extractive Q&A with citations, and unsupported-document guardrails exist

**Goals**
- Introduce retrieval-augmented generation (RAG)
- Enable safe, document-scoped Q&A
- Move the individual user experience from a linear results page to a document-centered conversation workspace

**Features**
- User-scoped document history/sidebar for returning to processed documents
- Active document workspace with upload, consent, summary, source excerpts, and Q&A
- Clause-level chunking and metadata tagging
- Embedding generation using transformer models
- Vector storage (pgvector or Qdrant)
- Grounded summary generation from clauses or extracted text
- Scoped question answering using retrieved clauses
- “I don’t know” responses when information is missing
- Unsupported-document state for `unknown` classification before chat or risk outputs appear

**ML & AI**
- Hugging Face embedding models
- Retrieval pipelines for clause selection
- LLM prompts constrained to retrieved context

**Success Criteria**
- LLM responses always reference document content
- Hallucinations are measurably reduced
- Users can ask targeted questions safely
- Users always know which document Lexi is answering from
- Unknown or unsupported documents are stopped gracefully
- Automated tests can run without paid or network LLM calls

---

## Infrastructure Gate — Data and Auth Before Public Beta

**Status:** Postgres gate implemented and passing against Docker Postgres with Alembic migrations

**Decisions**
- Keep PostgreSQL as the product database.
- Keep SQLite only for fast, isolated automated tests.
- Run the Postgres-backed E2E gate before public beta and release cuts.
- Keep custom JWT auth through private MVP.
- Use Supabase Auth for public beta while keeping FastAPI as the document-processing authority.

**Why this matters**
The current fast gates prove product behavior. A Postgres-backed gate proves migration and database fidelity before release. Supabase Auth removes a large amount of risky custom auth work when Lexi moves beyond private MVP.

**Success Criteria**
- Lease verification passes against Docker Postgres and Alembic migrations.
- Auth provider decision is made before external user onboarding.
- Supabase Auth is the public-beta path; FastAPI verifies Supabase JWTs and keeps ownership checks server-side.
- Custom-auth hardening remains intentionally deferred unless the Supabase path is reversed.

---

## Phase 3 — Risk Detection & Pattern Recognition

**Status:** First rule-based MVP slice complete; output-quality evaluation active

**Goals**
- Move from generic flags to smarter risk signals
- Surface patterns that deserve attention
- Establish premium risk intelligence without crossing into legal advice

**Features**
- Clause categorization (termination, fees, access, penalties)
- Detection of unusual or one-sided language
- Missing-section detection (expected but absent clauses)
- Comparative heuristics (common vs uncommon patterns)
- Advanced risk scoring and severity levels
- Confidence scoring across OCR, classification, extraction, and LLM outputs
- Prioritized “top risks” summary
- AI-generated negotiation or clarification questions

**ML & AI**
- PyTorch-based clause classifiers
- Fine-tuned transformer models for legal text
- Hybrid rule-based + ML risk scoring
- Candidate module names: `RiskSense`, `Lexi Risk Engine`, `/risk`

**Success Criteria**
- Risk flags feel helpful, not alarmist
- False positives are minimized
- Lexi clearly explains *why* something is flagged
- Severity and confidence help users prioritize attention without creating fear
- Early RiskSense outputs are evaluated against sample and real Ontario leases before advanced analytics are added

---

## Phase 4 — Risk Analytics & Forecasting

**Status:** Planned

**Goals**
- Add actuarial-style risk analytics for premium users and organizations
- Estimate practical exposure while staying informational
- Help users understand what could become expensive or time-sensitive

**Features**
- Financial impact estimation
- Lease comparison
- Renewal and penalty forecasting
- Document history and monitoring
- Pattern detection across a user’s documents
- Analytics API surface under `/analytics`

**Success Criteria**
- Analytics are explainable and source-grounded
- Estimates show assumptions and confidence
- Lexi prioritizes attention but never predicts legal outcomes

---

## Phase 5 — Multi-Document Support

**Status:** Planned

**Scope Expansion**
- Employment contracts
- Offer letters
- School enrollment and financial documents
- Government letters and notices

**Features**
- Document-type–specific pipelines
- Tailored summaries per document class
- Domain-aware risk heuristics

**ML & AI**
- Multi-class document classifiers
- Domain-specific tagging models
- Improved embedding strategies for mixed document types

**Success Criteria**
- New document types maintain Lexi’s clarity standards
- Safety boundaries remain intact
- Users trust Lexi across contexts

---

## Phase 6 — Language Access & Inclusion

**Status:** Planned

**Goals**
- Reduce language barriers without increasing risk

**Features**
- Multilingual plain-English explanations
- Translation of summaries (not source documents)
- Language-aware prompts and disclaimers

**ML & AI**
- Multilingual transformer models
- Controlled translation pipelines
- Language detection and confidence scoring

**Success Criteria**
- Translations preserve meaning and caution
- Lexi clearly signals translation limits
- Non-English speakers gain real understanding

---

## Phase 7 — Community & Ecosystem Integration

**Status:** Planned

**Goals**
- Connect understanding to real-world support
- Support ethical organization plans for tenant unions, student associations, nonprofits, and legal clinics

**Features**
- Export reports for legal clinics or tenant unions
- Shareable summaries with controlled access
- App-specific integrations (RiseUp, fLOKr)
- Community feedback loops (opt-in, anonymized)
- Bulk document analysis
- Aggregated anonymized risk trends
- Dashboards for recurring exploitative clauses
- Exportable advocacy and education reports

**ML & AI**
- Pattern aggregation (privacy-preserving)
- Feedback-informed model refinement
- Consent-aware analytics over anonymized document signals

**Success Criteria**
- Lexi complements human support systems
- No erosion of privacy or consent
- Community trust grows, not fragments
- Organization insights never expose individual user documents

---

## Phase 8 — Maturity & Governance

**Status:** Future

**Goals**
- Ensure long-term accountability and sustainability

**Features**
- Model evaluation dashboards
- Bias and error analysis
- Versioned explanations and audit logs
- Transparent model updates

**Success Criteria**
- Lexi remains explainable and inspectable
- Failures are visible and correctable
- Growth never compromises user safety

---

## What Lexi Will Never Do

Regardless of phase, Lexi will never:
- Provide legal advice
- Declare legality or illegality
- Predict outcomes in court or tribunals
- Hide uncertainty behind confident language
- Use premium features to block basic understanding
- Expose private documents through organization analytics

---

## Roadmap Philosophy

Lexi does not chase features.
Lexi earns trust.

If a feature increases confusion, risk, or false confidence, it does not ship.

Progress is measured not by speed, but by how many people walk away **better informed than before**.


---

## 🎯 Current Status & Next Actions (May 2026)

### ✅ Completed
- **Phase 0:** Foundations (architecture, documentation, safety boundaries)
- **Phase 1 Backend:** Foundational document upload and processing pipeline
  - Text extraction (PDF, DOCX, images with OCR)
  - Document classification (Ontario residential leases)
  - Clause parsing with 8 types
  - Metadata extraction
  - Security features (encryption, consent, deletion)
- **Backend runtime reliability:** Docker-backed local stack runs successfully
  - API, Celery worker, PostgreSQL, Redis, MinIO, and Qdrant
  - Migrations apply on API startup
  - Backend API gate passes with isolated test state
- **Phase 1.5 UI MVP:** First usable flow exists
  - Auth, upload, consent, polling, results, deletion, and print export
- **End-to-end lease verification:** First product proof gate passes
  - Backend API gate covers register/login → upload → consent → eager worker → results → delete
  - Live browser gate drives the Next.js UI against a live FastAPI test server
- **Early Phase 2:** RAG scaffolding, grounded backend summary display, document workspace, and limited Q&A exist
  - Chunking, embeddings, Qdrant adapter, deterministic test retrieval, `/ask` endpoint, fake summary provider, Ollama-compatible adapter, low-confidence fallback, summary persistence, sidebar/history, source excerpts, and citation-backed extractive Q&A
- **Phase 3 first slice:** Rule-based RiskSense exists
  - Source-grounded risk signals, confidence rollups, calm top-risk summaries, and workspace UI are implemented for supported Ontario lease results
- **Product documentation:** Current screenshots, sample lease images, user-testing materials, setup docs, and tracking docs are present

### ⚠️ Current Gap
The product is a working technical MVP, but not yet production-ready or user-validated.

Main gaps:
- Lexi’s output is not yet reliable or useful enough to carry private-beta value on its own
- Full natural-language Q&A should wait until extractive, citation-backed behavior stays stable
- Summaries, Q&A, source excerpts, and RiskSense need a focused output-quality pass against screenshots, sample scenarios, and real Ontario leases
- Extraction edge-case unit tests remain important, but are intentionally deferred until the expected output behavior is clearer

### 🚀 Immediate Priorities

#### Priority 1: Output Reliability and Usefulness
**Why First:** The platform works technically, but the screenshots show Lexi needs to produce clearer, more specific value before broader user testing.

**What to build:**
1. Review saved screenshots and sample lease outputs for vague, thin, repetitive, or overconfident responses
2. Strengthen plain-English summaries, source-backed facts, suggested questions, and missing-information behavior
3. Tune confidence and fallback language so weak extractions do not look more certain than they are
4. Keep all output grounded in source text and away from legal advice, legality claims, and outcome prediction

#### Priority 2: Real-Lease RiskSense Evaluation
**Why Second:** The first RiskSense slice is implemented, but it needs realistic lease examples before the signals can be trusted.

**What to build:**
1. Evaluate rule-based signals against real Ontario lease examples
2. Tune severity language and confidence thresholds from observed results
3. Capture false positives, missing signals, and unclear source excerpts
4. Keep basic risk flags informational and available without a paywall

#### Priority 3: User Testing
**Why Third:** The lease-understanding workspace needs validation with the people it is for after the output becomes more helpful.

**What to build:**
1. Run sessions with renters, students, newcomers, and community/legal support partners
2. Measure whether summaries, Q&A, and RiskSense reduce confusion
3. Capture where copy feels too confident, too vague, or too dense
4. Convert findings into public-beta hardening tasks

#### Priority 4: Public-Beta Auth Path and Operational Hardening
**Why Fourth:** Supabase is chosen and implemented, but auth and operations still need readiness checks before broader onboarding.

**Decision:**
1. Supabase Auth is the public-beta path.
2. FastAPI verifies Supabase JWTs and keeps document ownership checks server-side.
3. Custom auth remains private-MVP/local-E2E only unless this path is reversed.

**See:** `docs/product/user-testing.md` for session script, metrics, and analysis template.

### Timeline Overview

```
Done:       Backend/frontend MVP, document workspace, guarded Q&A, RiskSense first slice, screenshots
Now:        Output reliability and usefulness pass
Next:       Real-lease RiskSense evaluation
Then:       User testing and iteration
Later:      Public-beta hardening and monitoring
```

**Near-term target:** reliable private beta for Ontario residential leases.

---

# 🔗 Lexi — Integration Contract

This document defines how Lexi connects to, interacts with, and enhances external platforms such as RiseUp, fLOKr, and future systems.

It exists to ensure:
- User trust is preserved
- Data boundaries are respected
- Integrations remain simple, transparent, and safe

If an integration violates this document, it does not ship.

---

## Purpose

Lexi is not a platform.
Lexi is an **intelligence layer**.

Its role is to:
- Read documents
- Explain them clearly
- Highlight important details
- Support user understanding

Lexi does not:
- Own user workflows
- Replace host applications
- Make decisions on behalf of users

---

## Integration Philosophy

### 1. Assist, Don’t Take Over
Lexi enhances existing products without replacing them.

Host apps retain:
- Control
- UX ownership
- User relationships

Lexi provides:
- Document understanding
- Contextual explanations
- Structured outputs
- Risk intelligence outputs when explicitly enabled

---

### 2. Explicit User Consent

Lexi only processes documents when:

- a user explicitly uploads a file
**or**
- a user explicitly grants access to a document

No background scanning.
No silent ingestion.
No implicit consent.

---

### 3. Minimal Data Access

Lexi only accesses:
- The document provided
- Metadata required for processing

Lexi does not:
- Scrape user data
- Access unrelated files
- Persist unnecessary information

---

### 4. Transparent Processing

Users must always know:
- When Lexi is analyzing something
- What document is being processed
- What output is generated

No hidden operations.

---

## Integration Models

### 1. Direct Upload (Default)

User uploads a document directly into Lexi.

Flow:
1. User selects file
2. Lexi processes document
3. Lexi returns structured output

Used for:
- standalone usage
- privacy-first workflows

---

### 2. Embedded Integration (RiseUp / fLOKr)

Lexi is embedded inside a host app.

Examples:
- “Analyze Lease” button in renter app
- “Review Contract” inside onboarding flow

Flow:
1. User triggers Lexi explicitly
2. Document is passed securely
3. Lexi returns analysis to host UI

Lexi does not control UI.
Host app presents results.

---

### 3. API-Based Integration

External systems call Lexi via API.

Endpoints may include:
- `/analyze`
- `/summarize`
- `/flags`
- `/questions`
- `/risk`
- `/analytics`

All responses must be:
- Structured
- Explainable
- Grounded in source text

---

## Access & Plan Contract

### Free Tier
Free Lexi is for basic understanding.

It may include:
- Document upload
- OCR and text extraction
- Plain-English summaries
- Basic clause extraction
- Key dates and metadata
- Basic risk flags
- Limited document-scoped Q&A

Basic legal understanding must not be paywalled.

### Premium Risk Intelligence
Premium Lexi adds deeper risk intelligence.

It may include:
- Advanced risk scoring
- Severity levels for flagged clauses
- Confidence scoring across OCR, classification, extraction, and LLM outputs
- Financial impact estimation
- Lease comparison
- Renewal and penalty forecasting
- Pattern detection across documents
- Prioritized top risks
- Negotiation or clarification questions
- Document history and monitoring

Premium outputs must remain informational. They must not tell users what to do, predict outcomes, or declare legality.

### Organization Plans
Organization plans may support tenant unions, student associations, nonprofits, and legal clinics.

They may include:
- Aggregated anonymized risk trends
- Bulk document analysis
- Pattern detection across leases or contracts
- Dashboards for recurring exploitative clauses
- Exportable reports for advocacy, education, or clinic workflows

Organization analytics must be anonymized, consent-aware, and privacy-preserving.

---

## Data Handling Rules

### Temporary Processing

Documents are:
- Processed in-session
- Not stored long-term by default

Optional storage must be:
- Explicit
- User-approved

---

### Anonymization (Future)

Where possible:
- Remove identifying information
- Reduce sensitive exposure

Organization analytics require anonymization by default. Individual documents must not be exposed through dashboards, reports, exports, or trend views.

---

### No Training on User Data

User documents must not be used to:
- Train models
- Fine-tune systems

Unless:
- Explicit opt-in is provided

---

## Output Contract

All Lexi outputs must include:

### 1. Summary
- Plain-English explanation
- No legal jargon

### 2. Key Points
- Structured bullets
- One idea per point

### 3. Flagged Sections
- Referenced text
- Explanation
- Neutral tone

### 4. Questions
- Optional
- Non-prescriptive

### 5. Risk Intelligence
- Basic RiskSense attention signals may appear in standard document results
- Advanced analytics may be premium
- Severity, confidence, and assumptions clearly shown
- Source-grounded reasons for each flag
- Financial estimates labeled as estimates, not predictions
- Unsupported document types must not receive RiskSense output

---

## Safety Boundaries

Lexi must not:

- Give legal advice
- Predict legal outcomes
- Replace professional review
- Make decisions for users
- Use premium plans to block basic legal understanding
- Use analytics to pressure or scare users
- Expose user documents through organization insights

If confidence is low:

> “This section is unclear. You may want a legal clinic to review it.”

---

## Host App Responsibilities

Applications integrating Lexi must:

- Present outputs without distortion
- Preserve Lexi’s tone and intent
- Not reframe outputs as advice
- Not hide uncertainty indicators

---

## UX Integration Guidelines

Host apps should:

- Clearly label Lexi features
- Show when analysis is in progress
- Keep the active document visible when presenting Lexi answers
- Allow users to revisit outputs
- Provide access to original document context
- Present document Q&A as scoped to the selected document, not as a general
  legal chatbot
- Show an unsupported-document state when Lexi classifies a supported-format file
  as `unknown`

Avoid:
- Auto-triggering analysis
- Interrupting user workflows
- Overwhelming users with data
- Asking Lexi broad legal questions without an uploaded, processed, supported
  document

---

## Extensibility

Future integrations may include:

- Tenant support platforms
- Student services
- Newcomer assistance tools
- Financial agreement review systems

All must follow this contract.

---

## Versioning

This contract evolves with Lexi.

Changes must:
- Maintain user trust
- Not expand data access silently
- Be documented clearly

---

## Final Rule

Lexi integrates to:
- Clarify, not control
- Assist, not replace
- Inform, not decide

If an integration increases confusion, pressure, or opacity, it fails.

---

## Closing

Lexi exists across systems, but always stays the same:

- Transparent
- Bounded
- User-first

No matter where Lexi appears, it should feel like the same calm, reliable presence helping someone understand what matters.

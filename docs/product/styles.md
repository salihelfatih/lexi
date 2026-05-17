# 🎨 Lexi — Style & UX Guidelines

This document defines the **visual language, interaction patterns, and UX principles** for Lexi.

---

## Design Philosophy

Lexi is used in moments of:
- Uncertainty
- Pressure
- Confusion

The interface must feel:
- Calm
- Readable
- Grounded
- Non-intimidating

Lexi is not a dashboard.
Lexi is a reading companion.

For organization plans, analytics dashboards may exist, but they should still feel calm, restrained, and privacy-first. The individual user experience should remain a reading flow, not a command center.

---

## Core UX Principles

### 1. Clarity Over Density
No clutter. No overwhelming screens.

- One primary action per screen
- Progressive disclosure for complexity
- Break long outputs into sections

---

### 2. Calm Over Urgency
Avoid anything that feels like:
- Alerts
- Alarms
- Aggressive warnings

Lexi informs, it does not panic users.

---

### 3. Readability is Everything
Users are already dealing with dense legal text.

We reduce cognitive load by:
- Large, legible typography
- Generous spacing
- Clear hierarchy

---

### 4. Trust Through Transparency
Always show:
- What document is being analyzed
- What section is being referenced
- When something is uncertain

No “black box” feeling.

---

### 5. Assist, Don’t Automate Decisions
UI must never:
- Push users toward signing or rejecting
- Frame outputs as conclusions

Everything is framed as:
- Explanation
- Context
- Options

### 6. Access Is Ethical UX
Free Lexi must feel complete enough to help someone understand a document.

Premium entry points should offer deeper risk intelligence, not imply that basic understanding requires payment.

---

## Visual Identity

### Color Palette

#### Primary
- **Soft Indigo** `#4F46E5`
  - Used for primary actions and highlights
  - Feels calm and intelligent

#### Neutral Base
- **Background** `#FAFAFA`
- **Surface** `#FFFFFF`
- **Border** `#E5E7EB`
- **Text Primary** `#111827`
- **Text Secondary** `#6B7280`

#### Semantic (Soft, Never Aggressive)

- **Attention (Amber)** `#F59E0B`
- **Info (Blue)** `#3B82F6`
- **Safe/Neutral (Green)** `#10B981`

⚠️ Avoid harsh reds.
Risk is communicated through wording, not fear colors.

---

## Typography

### Font Stack
- Primary: `Inter`
- Fallback: `system-ui, sans-serif`

### Scale

- **Title**: 24–28px
- **Section Headers**: 18–20px
- **Body**: 15–16px
- **Helper Text**: 13–14px

### Rules
- Line height: 1.5–1.7
- Max width: ~70 characters per line
- Avoid dense paragraphs

---

## Layout System

### Spacing Scale
Use consistent spacing:
- 4 / 8 / 12 / 16 / 24 / 32 px

### Structure

Each analysis page should follow:

1. Document Header
2. Summary
3. Key Points
4. Flagged Sections
5. Questions You Can Ask

Never dump everything at once.

Phase 2 should shift this into a document-centered workspace:

1. Left sidebar: recent documents, processing state, upload entry point
2. Main header: active document name, status, confidence, delete/export actions
3. Main body: grounded summary, key details, source excerpts, and chat
4. Chat area: document-scoped questions with citations/source text
5. Unsupported state: clear recovery actions for `unknown` documents

The active document must remain visible while the user asks questions.

---

## Core UI Components

### 1. Document Upload

Simple and reassuring:

- Drag & drop zone
- “Upload a document to begin”
- Show file name after upload

No complex settings upfront.

---

### 2. Document History Sidebar

Used after sign-in for returning to previous processed documents.

Structure:
- Recent document list, scoped to the signed-in user
- Filename, classification/status, and last updated time
- Upload-new-document action
- Clear selected state for the active document

The sidebar is navigation, not an analytics dashboard.

---

### 3. Active Document Workspace

The main working surface for one document.

Include:
- Active document header
- Processing/consent state when needed
- Summary and key details after processing
- Source excerpts or clause links
- Document-scoped chat

Avoid:
- A blank chatbot as the first usable state
- Chat without an uploaded, processed, supported document
- Mixing user context with extracted document facts

---

### 4. Summary Card

The first thing users see.

Structure:
- Short paragraph (plain English)
- No jargon
- No bullet overload

---

### 5. Key Points Section

- Bullet-based
- Each point = one idea
- Optional “View source” link to document section

---

### 6. Flagged Sections

Displayed as soft-highlight cards.

Each includes:
- Excerpt from document
- Explanation
- Why it matters (optional)

Tone must stay neutral.

---

### 7. Question Suggestions and Chat

Framed as:
> “You could ask…”

Not:
> “You should…”

For chat:
- Use an input label such as "Ask about this document"
- Show citations or source excerpts with answers
- Say when the document does not contain the answer
- Keep optional situation context visually separate from answer evidence

---

### 8. Unsupported Document State

Used when classification returns `unknown`.

Copy should say:
> "Lexi could not identify this as a supported document type yet."

Include:
- Classification confidence
- Short explanation that Lexi currently supports Ontario residential leases
- Delete and upload-another actions
- No legal Q&A, RiskSense, or legality language

---

### 9. Risk Intelligence

Premium risk analytics should help users prioritize attention.

Use:
- Severity labels such as Low, Medium, High
- Confidence indicators with plain explanations
- Source links back to exact clauses
- “Why this matters” text
- Financial estimates with assumptions shown

Avoid:
- Fear-based colors or copy
- Final scores without explanation
- Legal conclusions
- “Sign” or “Do not sign” prompts

---

### 10. Organization Analytics

Organization dashboards may include anonymized trends, recurring clause patterns, bulk analysis, and exportable reports.

They must:
- Hide individual document content by default
- Make consent and anonymization status visible
- Use aggregate views before drill-downs
- Support advocacy and education workflows without exposing users

---

## Interaction Design

### Microinteractions

- Subtle hover states
- Smooth transitions (150–250ms)
- No flashy animations

---

### Loading States

Legal documents take time.

Use:
- Skeleton screens
- “Analyzing your document…” message

Never show:
- Spinning anxiety loops with no context

---

### Error Handling

Clear and human:

Bad:
> “Processing failed”

Good:
> “We couldn’t read this document clearly. You can try uploading a clearer version.”

---

## Accessibility

Minimum standards:

- WCAG AA contrast
- Keyboard navigation support
- Screen reader labels for all actions
- No color-only meaning

---

## Mobile Experience

Mobile is not optional.

Priorities:
- Vertical stacking
- Tap-friendly spacing
- Readable text without zoom

---

## What Lexi Avoids

- Complex dashboards for individual users
- Legal-style formatting
- Overuse of icons
- Bright or aggressive colors
- “AI magic” visuals

No glowing brains. No sci-fi nonsense.

---

## Visual Tone

If Lexi were a physical space, it would feel like:
- A quiet reading room
- Soft light
- Clean desk
- No noise

---

## Final Rule

If a design decision makes the interface:
- Faster but more confusing → reject it
- Prettier but less clear → reject it
- More impressive but less trustworthy → reject it

Lexi optimizes for:
**clarity, calm, and trust.**

---

## Closing

People come to Lexi when something matters.

The interface must:
- Reduce stress
- Increase understanding
- Preserve control

Good design here is not decoration.
It is protection.


---

## UI Implementation Guide

### Tech Stack

**Framework:** Next.js

**Core Libraries:**
- React
- Framer Motion
- Plain CSS design tokens in `app/globals.css`
- Local UI primitives in `app/components/ui/`

### Quick Setup

```bash
# Use the existing frontend workspace
cd frontend
npm install
npm run dev
```

Production:

```bash
cd frontend
npm run build
npm run start
```

### Project Structure

```
frontend/
├── app/
│   ├── page.jsx             # Home page
│   ├── layout.jsx           # Root layout
│   ├── globals.css          # Global styles
│   ├── lib/                 # API client
│   └── components/          # Product and UI components
├── next.config.mjs
└── package.json
```

### Implementation Phases

**Phase 1: Core Upload & Results**
- Auth
- Drag-and-drop upload
- Consent flow
- Processing status
- Results with metadata and clauses
- Delete and export

**Phase 2: Enhanced Understanding**
- Plain-English explanations (requires backend RAG)
- Limited document Q&A
- Document-centered workspace with sidebar/history
- Active document source panel or inline source excerpts
- Unsupported-document state for `unknown` classification
- Key dates timeline
- Suggested questions

**Phase 3: Risk Intelligence**
- Severity labels and confidence scoring
- Prioritized top risks
- Financial estimates with assumptions
- Lease comparison
- Renewal and penalty forecasting

**Phase 4: Organization Analytics**
- Anonymized aggregate trends
- Bulk analysis
- Recurring clause dashboards
- Exportable advocacy and clinic reports

### Success Criteria

- [ ] Users can upload documents without errors
- [ ] Processing completes in < 2 minutes
- [ ] Results are clear and readable
- [ ] Works on mobile devices
- [ ] 90%+ understand consent flow
- [ ] Premium risk intelligence never blocks free understanding
- [ ] Organization analytics never expose individual documents

---

*For detailed API contracts, see `docs/technical/contract.md`*

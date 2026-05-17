# Lexi User Testing Plan

## Goal

Validate whether target users can complete the Lexi MVP flow and understand results without assistance.

## Scope

This plan covers roadmap Priority 3:

1. Recruit 5-10 testers from target audience.
2. Test using real Ontario leases.
3. Observe real usage behavior.
4. Capture qualitative feedback.
5. Identify top 3 improvements.

## Execution Kit

Use the ready-to-run assets in `docs/product/testing-kit/`:

- `README.md` - testing kit overview and order
- `testing-playbook.md` - consolidated facilitation and templates
- `sample-lease-scenarios.md` - 5 Ontario lease scenarios for anonymized files
- `private-beta-checklist.md` - pre-wave operational checklist
- `05-recruitment-tracker.csv` - participant recruitment and scheduling
- `06-participant-log.csv` - consolidated participant outcomes
- `07-analysis-summary-template.md` - one-page synthesis template

## Recommended Execution Order

1. Fill `05-recruitment-tracker.csv` and schedule 5-10 participants.
2. Assign each participant a scenario from `sample-lease-scenarios.md`.
3. Clear the private-beta gate in `private-beta-checklist.md`.
4. Run setup and session flow from `testing-playbook.md`.
5. Capture outcomes in the scorecard section of `testing-playbook.md` and `06-participant-log.csv`.
6. Produce final one-page summary using `07-analysis-summary-template.md`.

## Target Participants

Recruit a mix of:

- Students renting for the first time
- Newcomers unfamiliar with Ontario lease wording
- Renters with prior lease disputes
- Users with low technical confidence

## Test Assets

Prepare:

- 3-5 anonymized Ontario lease scenario files with varied formatting
- One-page test moderator script
- Consent text for testing session recording
- Debrief form (5-10 minutes)
- Result scoring sheet

## Pre-Session Checklist

1. Verify backend API and worker are running.
2. Verify frontend app runs at `http://localhost:3000`.
3. Create test user accounts (or test account credentials).
4. Ensure each lease file is anonymized.
5. Ensure deletion flow is functioning before each session.

## Session Structure (30 minutes)

1. Intro (3 min)
- Explain this is product testing, not legal advice.
- Confirm user consent for observation notes.

2. Task Execution (20 min)
- Ask participant to complete flow without guidance:
  - Log in/register
  - Upload document
  - Provide consent settings
  - Wait for processing
  - Read results
  - Review RiskSense signals if shown
  - Ask one document-scoped question
  - Export report (print/save as PDF)
  - Delete document

3. Debrief (7 min)
- Ask clarity, trust, and usefulness questions.
- Capture confusion points and friction moments.

## Task Pass Criteria

A task is successful when completed without moderator intervention.

Track for each participant:

- Upload completed: yes/no
- Consent understood: yes/no
- Results interpreted correctly: yes/no
- Results found helpful: yes/no
- Q&A attempted: yes/no
- RiskSense helpful: yes/no/not shown
- Export action completed: yes/no
- Delete action completed: yes/no

## Quantitative Success Thresholds

Adopt roadmap thresholds:

- 80%+ complete upload successfully
- 90%+ understand consent flow
- 70%+ find results helpful
- Top 3 improvement areas identified

## Qualitative Interview Prompts

1. What part felt easiest?
2. What part felt confusing?
3. Did consent choices feel clear and fair?
4. Did the result summary help you understand your lease faster?
5. What would make this trustworthy enough to use again?

## Logging Template

For each participant record:

- Participant ID
- Device used (mobile/desktop)
- Browser
- Time to complete flow
- Failed step(s)
- Verbatim confusion quote
- Suggested fix
- Top UX issue
- Top trust/safety issue

## Analysis Method

1. Aggregate failure counts by step.
2. Group confusion into themes.
3. Prioritize fixes by:
- frequency
- severity
- implementation effort

## Output Deliverable

After testing, produce a one-page summary:

- Metrics versus thresholds
- Top 3 UX issues
- Recommended fixes for next sprint
- Go/no-go recommendation for wider pilot

## Safety Notes

- Do not upload production personal data.
- Keep testing leases anonymized.
- Delete all uploaded docs after each session.

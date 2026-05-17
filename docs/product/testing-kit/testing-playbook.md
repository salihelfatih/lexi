# Lexi Testing Playbook

This playbook consolidates session preparation, facilitation, consent, scoring, and synthesis.

## 1. Purpose

Validate whether users can complete the Lexi MVP flow and understand outputs without assistance.

## 2. Session Timing (30 min)

1. Intro and consent: 3 min
2. Task execution: 20 min
3. Debrief: 7 min

## 3. Before Each Session

### Technical checks

1. Clear `private-beta-checklist.md` for the testing wave.
2. Start API, worker, and frontend.
3. Confirm `http://localhost:8000/docs` and `http://localhost:3000` are reachable.
4. Run one smoke flow: upload -> consent -> processing -> results -> Q&A -> delete.
5. Confirm test credentials are ready.
6. Confirm the assigned scenario from `sample-lease-scenarios.md`.
7. Confirm lease file is anonymized.

### Materials

- Participant ID
- One anonymized Ontario lease file
- Scenario ID
- Consent script (section 4)
- Session scorecard (section 7)
- Debrief prompts (section 8)

## 4. Session Consent Script

Read verbatim:

We are conducting a product usability session for Lexi.

Purpose:
- Understand what is clear and what is confusing
- Identify improvements for the next sprint

What we collect:
- Task outcomes
- Timing and usability notes
- Verbal feedback in debrief

What we do not collect:
- Legal advice from you
- Personal legal details beyond the test scenario

Privacy:
- Notes use participant ID, not your name
- Test files are anonymized
- Uploaded test files are deleted after the session

Participation:
- Participation is voluntary
- You can skip any question
- You can stop at any time

Lexi boundary:
- Lexi provides legal information, not legal advice

Do you consent to proceed?

[ ] Yes
[ ] No

## 5. Moderator Script

### Opening

"Thanks for joining. We are testing the product, not you. There are no right or wrong answers. Please think out loud as you go."

### Task prompt

"Please complete this flow as if this were your own lease. I will only help if you are blocked for a while."

Tasks:

1. Log in or register
2. Upload the provided lease
3. Choose consent settings
4. Wait for processing completion
5. Review and explain results in your own words
6. Review any RiskSense attention signals
7. Ask one question about the document
8. Export report (print or save as PDF)
9. Delete the uploaded document

Facilitation rules:

- Stay neutral
- If blocked for over 90 seconds, log first, then assist
- Capture confusion quotes verbatim when possible

## 6. Task Success Rules

A task counts as success only if completed with no moderator intervention.

Track for each participant:

- Upload completed: yes/no
- Consent understood: yes/no
- Results interpreted correctly: yes/no
- Results found helpful: yes/no
- Q&A answer useful: yes/no/not attempted
- RiskSense useful: yes/no/not shown
- Export completed: yes/no
- Delete completed: yes/no

## 7. Session Scorecard Template

Participant ID:
Scenario ID:
Date:
Moderator:

Task outcomes:

1. Log in/register: [ ] Success [ ] Success with intervention [ ] Failed
2. Upload document: [ ] Success [ ] Success with intervention [ ] Failed
3. Provide consent settings: [ ] Success [ ] Success with intervention [ ] Failed
4. Reach processing complete state: [ ] Success [ ] Success with intervention [ ] Failed
5. Interpret results correctly: [ ] Success [ ] Success with intervention [ ] Failed
6. Review RiskSense: [ ] Success [ ] Success with intervention [ ] Failed [ ] Not shown
7. Ask a document-scoped question: [ ] Success [ ] Success with intervention [ ] Failed [ ] Not attempted
8. Export report: [ ] Success [ ] Success with intervention [ ] Failed
9. Delete document: [ ] Success [ ] Success with intervention [ ] Failed

Timing:

- Start time:
- End time:
- Total completion time:

Top frictions:

1.
2.
3.

Trust and safety notes:

1.
2.

## 8. Debrief Prompts

1. What part felt easiest?
2. What part felt confusing?
3. Did consent choices feel clear and fair?
4. Did results help you understand the lease faster?
5. Did the RiskSense signals feel useful, too strong, too vague, or about right?
6. Did the answer citations make the Q&A feel more trustworthy?
7. What would make this trustworthy enough to use again?

Optional probes:

- What did you expect to happen at that step?
- What wording would make this clearer?

## 9. Analysis and Synthesis

Use `06-participant-log.csv` for aggregate analysis and fill `07-analysis-summary-template.md`.

Prioritization rules:

1. Frequency
2. Severity
3. Effort

## 10. Escalation Conditions

Pause sessions and notify engineering if:

- Upload fails for two participants in a row
- Consent flow is unclear or inaccessible
- Processing hangs beyond 5 minutes
- Results include legality claims, legal-advice language, or outcome prediction
- Delete action fails

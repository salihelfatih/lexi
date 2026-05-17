# Ontario Lease Scenario Set

Use these scenarios to prepare anonymized Ontario residential lease files for observed sessions. Each file should be a PDF or DOCX that contains only fictional names, addresses, emails, phone numbers, and payment details.

These are facilitator scenarios, not legal examples or legal advice. The goal is to see whether users understand Lexi's flow, summaries, RiskSense signals, and document-scoped Q&A.

## Scenario UT-01: Standard First Apartment Lease

Participant fit: first-time renter or student.

Document shape:
- Ontario residential lease with clear landlord, tenant, address, rent, start date, end date, maintenance, entry, utilities, and subletting sections.
- Clean selectable-text PDF or DOCX.
- Few formatting surprises.

Expected Lexi behavior:
- Classifies as `ontario_residential_lease`.
- Extracts tenant, landlord, property address, rent, and dates.
- Shows grounded summary and basic RiskSense attention signals.
- Q&A can answer rent, dates, maintenance, entry, utilities, and subletting questions.

Questions to prompt if the participant stalls:
- What is the monthly rent?
- When does this lease end?
- What does the document say about landlord entry?

Primary thing to observe:
- Can the participant complete the full flow without help and explain the results in their own words?

## Scenario UT-02: Fees and Utility Responsibility

Participant fit: renter with some prior rental experience.

Document shape:
- Ontario residential lease with clear rent, plus clauses about late fees, service charges, utilities, and payment timing.
- Include language that is broad enough to deserve attention but avoid obviously extreme wording.

Expected Lexi behavior:
- Extracts monthly rent and dates.
- RiskSense should surface extra charge, rent timing, or utility responsibility signals when the source text supports them.
- Summary should remain calm and avoid legality claims.

Questions to prompt if the participant stalls:
- What costs are described besides monthly rent?
- Does the lease say who pays utilities?
- Which RiskSense signal feels most useful or least useful?

Primary thing to observe:
- Do RiskSense labels and confidence scores help prioritize review without making the participant feel pushed toward a decision?

## Scenario UT-03: Entry and Maintenance Ambiguity

Participant fit: renter with prior confusion or dispute around repairs or access.

Document shape:
- Ontario residential lease with a landlord entry clause, inspection wording, repair responsibilities, and tenant maintenance obligations.
- Use one or two clauses with ambiguous wording that a user may want to clarify.

Expected Lexi behavior:
- Shows source-grounded RiskSense signals for entry or maintenance when matched.
- Q&A cites document text instead of giving general legal rules.
- Missing or unclear obligations are described as unclear or not found, not invented.

Questions to prompt if the participant stalls:
- What does this document say about repairs?
- What does it say about landlord entry?
- What would you want to clarify before signing?

Primary thing to observe:
- Does the participant trust the answer more when citations or source excerpts are visible?

## Scenario UT-04: Messy Formatting, Still Supported

Participant fit: low technical confidence user or mobile user.

Document shape:
- Ontario residential lease exported from a scan or image-heavy PDF.
- Include real-world spacing issues, page breaks, and inconsistent numbering.
- Keep text quality good enough that Lexi should classify it as supported.

Expected Lexi behavior:
- Completes processing without hanging.
- Extraction confidence may be lower than clean examples.
- Summary and Q&A stay conservative if source quality is uneven.

Questions to prompt if the participant stalls:
- Did the processing state make it clear that Lexi was still working?
- Do the confidence indicators affect how much you trust the result?
- Is anything missing that you expected Lexi to find?

Primary thing to observe:
- Can users recover from imperfect extraction without losing trust or assuming Lexi is certain?

## Scenario UT-05: Missing Detail Check

Participant fit: newcomer or participant unfamiliar with lease structure.

Document shape:
- Ontario residential lease with common fields present, but intentionally omit or obscure one expected detail such as parking, key deposit, or a specific utility responsibility.
- Keep the omission realistic and anonymized.

Expected Lexi behavior:
- Extracts present facts and marks missing values as not found.
- Q&A responds with "I don't know from this document" or equivalent grounded uncertainty when asked about omitted details.
- RiskSense does not fill gaps with assumptions.

Questions to prompt if the participant stalls:
- Does this document say parking is included?
- What does Lexi do when the answer is not in the document?
- Did that response feel clear, too vague, or trustworthy?

Primary thing to observe:
- Do users understand that "not found" is a safety boundary rather than a product failure?

## Sample Asset Notes

The image mocks in `docs/media/samples/` can help with facilitator preparation and visual examples. For live sessions, use anonymized PDF or DOCX lease files that match the scenario descriptions above, because the current user flow is designed around uploadable documents.

Before every session:
- Remove real names, addresses, phone numbers, emails, account numbers, and signatures.
- Confirm the file opens locally before upload.
- Run one smoke upload with a facilitator test account.
- Delete the smoke-test upload before the participant starts.

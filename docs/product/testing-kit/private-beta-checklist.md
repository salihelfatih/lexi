# Private Beta Testing Checklist

Use this before inviting each wave of user testers. The checklist is intentionally operational: if an item is not ready, pause sessions or narrow the participant group.

## 1. Product Gate

- [ ] Backend API gate passes in the `lexi` Python environment.
- [ ] Live browser lease-verification gate passes with RiskSense assertions.
- [ ] Postgres-backed E2E gate has passed for the current release candidate or has a documented reason for deferral.
- [ ] Unsupported-document flow has been smoke-tested.
- [ ] Delete flow has been smoke-tested after a completed result.

## 2. Test Environment

- [ ] Backend API, worker, database, Redis, and frontend are reachable.
- [ ] Test auth provider is intentional for the session: custom for private-MVP local testing, Supabase for public-beta rehearsal.
- [ ] `LLM_PROVIDER=fake` or another approved provider is set deliberately.
- [ ] Upload temp storage is shared between API and worker.
- [ ] No production personal documents are present in the test account.

## 3. Test Materials

- [ ] Participant has a unique participant ID.
- [ ] Participant is assigned one scenario from `sample-lease-scenarios.md`.
- [ ] Lease file is anonymized and opens locally.
- [ ] Moderator has the consent script ready.
- [ ] Moderator has `06-participant-log.csv` open before the session starts.
- [ ] Backup lease file is available if upload fails because of file damage.

## 4. Session Safety

- [ ] Participant understands this is product testing, not legal advice.
- [ ] Participant consents to observation notes.
- [ ] Recording consent is captured separately if recording is used.
- [ ] Moderator will not ask for personal legal facts.
- [ ] Moderator will stop the session if the participant uploads a real personal document by mistake.

## 5. Success Metrics

- [ ] Upload completion is recorded as yes/no.
- [ ] Consent understanding is recorded as yes/no.
- [ ] Results helpfulness is recorded as yes/no.
- [ ] Q&A usefulness is recorded when attempted.
- [ ] RiskSense usefulness is recorded when visible.
- [ ] Top UX issue and top trust/safety issue are captured before the next session starts.

## 6. Halt Conditions

Pause the testing wave and notify engineering if any condition occurs:

- [ ] Upload fails for two participants in a row.
- [ ] Consent is misunderstood by two participants in a row.
- [ ] Processing hangs beyond 5 minutes on a supported lease.
- [ ] Results show legal-advice language, legality claims, or outcome prediction.
- [ ] A participant cannot delete their document.
- [ ] Cross-account document access is suspected.

## 7. After Each Session

- [ ] Delete the uploaded document from Lexi.
- [ ] Clear local downloaded or printed test artifacts.
- [ ] Complete the participant log while details are fresh.
- [ ] Mark any severe issue for same-day triage.
- [ ] Update the analysis summary with emerging top themes.

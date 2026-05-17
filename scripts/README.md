# Scripts

Small helper scripts for contributors.

## Onboarding

Use these in order from the repository root:

1. `scripts/onboarding/setup-dev.sh`
2. `scripts/onboarding/start-dev.sh`
3. `scripts/onboarding/check-health.sh`
4. `python3 scripts/onboarding/validate-setup.py`

## Notes

- Scripts are safe to re-run.
- Setup uses `mamba` when available and falls back to `conda`.
- Backend services run through Docker Compose for a consistent API, worker, database, cache, object storage, and vector store.
- Frontend onboarding starts Next.js local dev (`npm run dev`) and auto-cleans stale dev processes on port conflicts.
- Scripts print clear next steps when dependencies are missing.
- For full background, see `docs/technical/SETUP.md`.

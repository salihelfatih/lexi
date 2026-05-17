# Contributing to Lexi

Lexi helps people understand legal documents safely, clearly, and without pretending to be a lawyer.

This project is open to contributors who care about access, privacy, careful AI, plain language, and community protection.

## Start Here

1. Read the [README](README.md) for the mission and product shape.
2. Read the [roadmap](docs/product/roadmap.md) to see what is planned and what is current.
3. Follow the [setup guide](docs/technical/SETUP.md).
4. Run the health checks before opening a pull request.

Recommended local setup:

```bash
./scripts/onboarding/setup-dev.sh
./scripts/onboarding/start-dev.sh
./scripts/onboarding/check-health.sh
python3 scripts/onboarding/validate-setup.py
```

The setup script uses `mamba` when available and falls back to `conda`. Docker is used for the backend runtime.

## Good First Contribution Areas

- Backend reliability: tests, migrations, Docker health, Celery task flow
- End-to-end coverage: upload, consent, processing, results, deletion
- Frontend accessibility: forms, focus states, mobile polish, clearer error states
- Plain-language UX: calmer copy, better uncertainty wording, less jargon
- Document processing: extraction edge cases, OCR confidence, metadata validation
- RAG safety: grounded retrieval, citation checks, "not found" behavior
- RiskSense: severity labels, confidence rollups, top-risk summaries
- Documentation: setup fixes, architecture notes, user-testing materials

## What Not To Add

Please do not contribute features that:

- Present Lexi as legal advice
- Tell users what legal action to take
- Declare that a clause is legal or illegal
- Inflate risk language to scare users
- Upload or commit real user documents
- Expose identifiable document details in analytics
- Put basic understanding behind a paywall

Lexi can highlight, explain, and prioritize. It should not pretend to adjudicate.

## Development Workflow

Backend stack:

```bash
docker compose up -d --build api worker
docker compose ps
curl http://localhost:8000/health
```

Backend tests:

```bash
docker compose exec -T api pytest backend/tests -q
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Local Python environment:

```bash
mamba env update -n lexi -f environment.yml --prune
mamba run -n lexi pytest backend/tests -q
```

Use `conda` for the same commands if `mamba` is not installed.

## Pull Request Checklist

Before opening a PR:

- Keep the change focused and tied to the roadmap or an issue.
- Add or update tests when behavior changes.
- Update docs when setup, API behavior, or product direction changes.
- Run backend tests and relevant frontend checks.
- Do not commit secrets, local env files, generated caches, or real legal documents.
- Use cautious, information-only language for legal/risk features.

## Data and Privacy

Use synthetic, public-domain, or clearly anonymized sample documents only.

Do not commit:

- Real leases or contracts from users
- Names, addresses, account details, signatures, or private messages
- API keys, tokens, credentials, or local Docker/Conda config

If a test needs a document fixture, prefer a small synthetic file that exercises one clear behavior.

## Product Judgment

When in doubt, choose the option that makes Lexi:

- More grounded in the uploaded document
- More honest about uncertainty
- Easier for a non-expert to understand
- Safer for vulnerable users
- Less likely to overclaim

The bar is not "does this sound smart?" The bar is "does this help someone avoid a bad decision without misleading them?"

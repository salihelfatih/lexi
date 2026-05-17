#!/usr/bin/env bash
set -euo pipefail

# Quick health checks for local dev.
# Run from repository root: ./scripts/onboarding/check-health.sh

check_url() {
  local name="$1"
  local url="$2"
  if curl -fsS "$url" >/dev/null 2>&1; then
    echo "OK: $name ($url)"
  else
    echo "NOT READY: $name ($url)"
  fi
}

echo "Running health checks..."
check_url "Backend health" "http://localhost:8000/health"
check_url "Backend docs" "http://localhost:8000/docs"
check_url "Frontend" "http://localhost:3000"
check_url "Qdrant" "http://localhost:6333/healthz"

echo "Done."

#!/usr/bin/env bash
set -euo pipefail

# Starts API, worker, and frontend in separate terminals.
# Run from repository root: ./scripts/onboarding/start-dev.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
else
  echo "Missing Docker Compose command (docker-compose or docker compose)."
  echo "Please install Docker Compose, then run this script again."
  exit 1
fi

echo "Starting Docker backend services..."
$COMPOSE_CMD up -d --build api worker

echo "Backend services started."
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"

if ! command -v x-terminal-emulator >/dev/null 2>&1 && ! command -v gnome-terminal >/dev/null 2>&1; then
  echo "No supported terminal launcher found."
  echo "Run the frontend manually:"
  echo "  cd frontend && npm run dev"
  exit 0
fi

launch_cmd() {
  local title="$1"
  local cmd="$2"
  if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal --title="$title" -- bash -lc "$cmd; exec bash"
  else
    x-terminal-emulator -T "$title" -e bash -lc "$cmd; exec bash"
  fi
}

launch_cmd "Lexi Frontend" "cd '$ROOT_DIR/frontend' && pkill -f \"next dev\" || true; pkill -f \"npm run dev\" || true; npm run dev"

echo "Backend is running in Docker; frontend started in a separate terminal."
echo "Next: run ./scripts/onboarding/check-health.sh"

#!/usr/bin/env bash
set -euo pipefail

# Inclusive, direct setup for local development.
# Run from repository root: ./scripts/onboarding/setup-dev.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

SPACY_MODEL_URL="https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl"

echo "[1/6] Checking required tools..."
for cmd in npm docker; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required tool: $cmd"
    echo "Please install it, then run this script again."
    exit 1
  fi
done

find_env_manager() {
  local candidate

  if command -v mamba >/dev/null 2>&1; then
    command -v mamba
    return 0
  fi

  for candidate in \
    "$HOME/.local/miniforge3/bin/mamba" \
    "$HOME/miniforge3/bin/mamba" \
    "$HOME/mambaforge/bin/mamba" \
    "$HOME/miniconda3/bin/mamba" \
    "$HOME/anaconda3/bin/mamba"; do
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  if command -v conda >/dev/null 2>&1; then
    command -v conda
    return 0
  fi

  for candidate in \
    "$HOME/.local/miniforge3/bin/conda" \
    "$HOME/miniforge3/bin/conda" \
    "$HOME/mambaforge/bin/conda" \
    "$HOME/miniconda3/bin/conda" \
    "$HOME/anaconda3/bin/conda"; do
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}

if ! ENV_MANAGER="$(find_env_manager)"; then
  echo "Missing Python environment manager: mamba or conda"
  echo "Install Miniforge/Mambaforge or add mamba/conda to PATH, then run this script again."
  exit 1
fi

if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
else
  echo "Missing Docker Compose command (docker-compose or docker compose)."
  echo "Please install Docker Compose, then run this script again."
  exit 1
fi

echo "[2/6] Preparing Python environment with $ENV_MANAGER..."

if "$ENV_MANAGER" env list | awk '{print $1}' | grep -qx "lexi"; then
  "$ENV_MANAGER" env update -n lexi -f environment.yml --prune
else
  "$ENV_MANAGER" env create -f environment.yml
fi

echo "[3/6] Installing spaCy model..."
"$ENV_MANAGER" run -n lexi python -m pip install "$SPACY_MODEL_URL"

echo "[4/6] Preparing frontend dependencies..."
cd "$ROOT_DIR/frontend"
npm install

cd "$ROOT_DIR"
echo "[5/6] Building and starting Docker backend services..."
$COMPOSE_CMD up -d --build api worker

echo "[6/6] Verifying backend container health..."
$COMPOSE_CMD ps

echo "Setup complete."
echo "Next: run ./scripts/onboarding/start-dev.sh"

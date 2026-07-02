#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv is required to run this skill package test entrypoint." >&2
  exit 2
fi

cd "$(dirname "$0")/.."
uv sync --python 3.14
uv run python --version
uv run ruff check scripts
uv run python scripts/run_evals.py --validate
uv run python scripts/run_evals.py --json
uv run python -m unittest discover -s scripts/tests -v
uv run python scripts/validate-skill-package.py .

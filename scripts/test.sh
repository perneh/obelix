#!/usr/bin/env bash
# Obelix test runner — thin wrapper around pytest.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

run_pytest() {
  if [[ -d .venv ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  fi
  pytest "$@"
}

case "${1:-all}" in
  all)
    run_pytest
    ;;
  unit)
    run_pytest backend/tests/unit -m unit
    ;;
  integration)
    run_pytest backend/tests/integration -m "integration and not live"
    ;;
  live)
    shift
    run_pytest backend/tests/integration -m live "$@"
    ;;
  regression)
    shift
    run_pytest backend/tests/regression -m regression "$@"
    ;;
  cov)
    run_pytest --cov=app --cov-report=term-missing
    ;;
  *)
    run_pytest "$@"
    ;;
esac

#!/usr/bin/env bash
# Recreate a new auxiliary Python 3.12 environment. Never target the active venv.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${PCCAP_SETUP_PYTHON:-python3.12}" -B "$SCRIPT_DIR/setup_venv.py" "$@"

#!/usr/bin/env bash
# Integration gate. Must pass before merging anything to main.
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
[ -x "$PY" ] || PY=.venv/Scripts/python.exe   # Windows (Git Bash)
export PYTHONPATH="src:."
"$PY" -m pytest -q tests
"$PY" -m finagent.run

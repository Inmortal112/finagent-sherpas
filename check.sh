#!/usr/bin/env bash
# Integration gate. Must pass before merging anything to main.
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
SEP=":"
if [ ! -x "$PY" ]; then
  PY=.venv/Scripts/python.exe   # Windows (Git Bash)
  SEP=";"                       # Windows Python splits PYTHONPATH on ';', not ':'
fi
export PYTHONPATH="src${SEP}."
"$PY" -m pytest -q tests
"$PY" -m finagent.run

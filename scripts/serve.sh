#!/usr/bin/env bash
# Start the backend so other devices can reach it. Usage: scripts/serve.sh [port]
#   - this computer:        http://localhost:PORT/chat
#   - a phone on the Wi-Fi: http://<address printed below>:PORT/chat  (the microphone needs https: see share.sh)
set -euo pipefail
cd "$(dirname "$0")/.."
PORT="${1:-8000}"
PY=.venv/bin/python
[ -x "$PY" ] || PY=.venv/Scripts/python.exe
[ -d out ] || PYTHONPATH="src:." "$PY" -m finagent.run >/dev/null
ADDRESS="$(hostname -I 2>/dev/null | cut -d' ' -f1 || true)"
echo "On this computer:  http://localhost:${PORT}/chat"
[ -n "$ADDRESS" ] && echo "On the same Wi-Fi: http://${ADDRESS}:${PORT}/chat"
PYTHONPATH="src:." exec "$PY" -m uvicorn finagent.server:app --host 0.0.0.0 --port "$PORT"

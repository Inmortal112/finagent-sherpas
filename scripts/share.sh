#!/usr/bin/env bash
# A temporary public https link to the backend running on this computer (start it first: scripts/serve.sh).
# Usage: scripts/share.sh [port]
# It opens an SSH tunnel through localhost.run: nothing to install and no account. The link is printed
# below, works while this command runs, and changes every time. Anyone with the link can ask questions,
# which spends team credits: the caps are ASK_MAX_TURNS and ASK_MAX_PER_MINUTE in .env.
set -euo pipefail
PORT="${1:-8000}"
curl -fsS -m 3 "http://localhost:${PORT}/healthz" >/dev/null || { echo "Nothing on port ${PORT}: run scripts/serve.sh first" >&2; exit 1; }
exec ssh -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 -R "80:localhost:${PORT}" nokey@localhost.run

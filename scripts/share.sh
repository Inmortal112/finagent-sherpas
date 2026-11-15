#!/usr/bin/env bash
# A temporary public https link to the backend running on this computer (start it first: scripts/serve.sh).
# Usage: scripts/share.sh [port]
# The link is printed below, works while this command runs, and changes every time. Anyone with the link
# can ask questions, which spends team credits: the caps are ASK_MAX_TURNS and ASK_MAX_PER_MINUTE in .env.
#
# Two ways, the first one found is used:
#   1. cloudflared (Cloudflare quick tunnel, no account). Fast enough for the voice: measured on
#      2026-11-15, a 398 KB answer arrived in 0.3 s. Install: `winget install Cloudflare.cloudflared`,
#      `brew install cloudflared`, or https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
#   2. An SSH tunnel through localhost.run: nothing to install, but slow. Measured the same day at about
#      5 KB/s: the page took 22 s and the spoken answers (128 kbps mp3) could not play without cuts.
set -euo pipefail
PORT="${1:-8000}"
# 127.0.0.1, not localhost: on Windows localhost can resolve to ::1, where uvicorn (0.0.0.0) is not listening.
curl -fsS -m 3 "http://127.0.0.1:${PORT}/healthz" >/dev/null || { echo "Nothing on port ${PORT}: run scripts/serve.sh first" >&2; exit 1; }
CLOUDFLARED="$(command -v cloudflared || true)"
for candidate in "/c/Program Files (x86)/cloudflared/cloudflared.exe" "/c/Program Files/cloudflared/cloudflared.exe"; do
  [ -z "$CLOUDFLARED" ] && [ -x "$candidate" ] && CLOUDFLARED="$candidate"   # winget does not always add it to PATH
done
if [ -n "$CLOUDFLARED" ]; then
  exec "$CLOUDFLARED" tunnel --no-autoupdate --url "http://127.0.0.1:${PORT}"
fi
echo "cloudflared not found: using localhost.run, which is too slow for the voice (see the top of this file)" >&2
exec ssh -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes \
  -R "80:127.0.0.1:${PORT}" nokey@localhost.run

#!/usr/bin/env bash
# AstroBaba launcher for macOS / Linux: sets up a private Python environment once, then starts the app.
set -e
cd "$(dirname "$0")"
PORT="${PORT:-8000}"
PY="${PYTHON:-python3}"
command -v "$PY" >/dev/null || { echo "Python 3.10+ is required. Install it from python.org, then run this again."; exit 1; }
if [ ! -d .venv ]; then
  echo "First run: setting up (this takes a minute)..."
  "$PY" -m venv .venv
  . .venv/bin/activate
  pip install --quiet --upgrade pip
  # pyswisseph builds from source; newer setuptools breaks its build, so pin an older one
  pip install --quiet "setuptools<70" wheel
  pip install --quiet --no-build-isolation pyswisseph || {
    echo "Could not build the astronomy library. It needs a C compiler:"
    echo "  macOS: xcode-select --install     Ubuntu/Debian: sudo apt install build-essential python3-dev"
    rm -rf .venv; exit 1; }
  pip install --quiet fastapi "uvicorn[standard]" tzdata
else
  . .venv/bin/activate
fi
URL="http://localhost:$PORT"
echo "AstroBaba is starting at $URL  (press Ctrl+C to stop)"
[ -z "$NO_OPEN" ] && { (sleep 2; (command -v open >/dev/null && open "$URL") || (command -v xdg-open >/dev/null && xdg-open "$URL") || true) >/dev/null 2>&1 & }
exec uvicorn api.main:app --port "$PORT"

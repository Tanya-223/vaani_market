#!/usr/bin/env bash
# Start the Vaani Market web app. Usage: ./run_web.sh [port]
set -e
cd "$(dirname "$0")"
. .venv/bin/activate
exec python -W ignore src/vaani/web/app.py "${1:-8000}"

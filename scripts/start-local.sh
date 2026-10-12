#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
.venv/bin/python -m portal.worker &
worker_pid=$!
.venv/bin/python -m portal.jobs &
documents_pid=$!
trap 'kill "$worker_pid" "$documents_pid" 2>/dev/null || true' EXIT INT TERM
.venv/bin/python -m portal.app

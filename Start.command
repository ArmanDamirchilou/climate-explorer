#!/bin/zsh
set -eu
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then
  if ! command -v python3.14 >/dev/null 2>&1; then
    print -u2 'Python 3.14 is required. Install it, then run this file again.'
    exit 1
  fi
  python3.14 -m venv .venv
  .venv/bin/python -m pip install -r requirements-lock.txt
fi
exec .venv/bin/python server.py

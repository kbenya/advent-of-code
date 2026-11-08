#!/usr/bin/env bash
# Runs aoc_tool.py with whichever Python works on this machine

if python3 -c "" 2>/dev/null; then
    PY=python3     # Linux / macOS
else
    PY=python      # Windows (python3 there is often a fake Store link)
fi

exec "$PY" "$(dirname "$0")/aoc_tool.py" "$@"

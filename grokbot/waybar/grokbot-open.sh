#!/usr/bin/env bash
set -euo pipefail
# Execute a fixed app name; never eval user input or infer an executable from a class.
if command -v grokbot >/dev/null 2>&1; then
    grokbot >/dev/null 2>&1 || true
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open 'https://grok.com/' >/dev/null 2>&1 || true
fi

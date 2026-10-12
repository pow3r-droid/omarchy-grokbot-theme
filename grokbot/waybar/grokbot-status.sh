#!/usr/bin/env bash
set -euo pipefail
if command -v grokbot >/dev/null 2>&1; then
    printf '%s\n' '{"text":"◈ GB","tooltip":"Grok Bot app available · SUPER+G scratchpad","class":"ready"}'
else
    printf '%s\n' '{"text":"◈ GB","tooltip":"Grok Bot web launcher · app executable not found","class":"standby"}'
fi

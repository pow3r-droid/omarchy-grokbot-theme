#!/usr/bin/env bash
set -euo pipefail
for dependency in grim slurp wl-copy; do
    if ! command -v "$dependency" >/dev/null 2>&1; then
        printf 'Grok Bot: screenshot unavailable; missing %s\n' "$dependency" >&2
        exit 0
    fi
done
region=$(slurp 2>/dev/null) || exit 0
[[ -n $region ]] || exit 0
# A single capture to the clipboard; no on-disk screenshot or persistent process.
grim -g "$region" - | wl-copy --type image/png || true

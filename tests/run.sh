#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
mapfile -d '' scripts < <(find "$root" -path "$root/.git" -prune -o -type f \( -name '*.sh' -o -path "$root/bin/omarchi-grokbot" \) -print0)
for script in "${scripts[@]}"; do bash -n "$script"; done
if command -v shellcheck >/dev/null 2>&1; then
    shellcheck "${scripts[@]}"
else
    echo 'SKIP: ShellCheck unavailable; Bash syntax checks passed.'
fi
python3 "$root/tests/validate_theme.py"

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
# Omarchy 4 Lua configs: syntax check plus a stubbed load of grokbot.lua.
if command -v luac >/dev/null 2>&1; then
    luac -p "$root/hyprland.lua" "$root/grokbot/hyprland/grokbot.lua" "$root/neovim.lua"
    lua - "$root" <<'LUA'
local root = arg[1]
local binds, rules, unbinds = {}, {}, {}
o = { bind = function(k, d, c) binds[k] = c end, window = function(m, r) rules[#rules+1] = {m, r} end }
hl = { unbind = function(k) unbinds[#unbinds+1] = k end, config = function() end,
       dsp = { workspace = { toggle_special = function(n) return "special:" .. n end } } }
dofile(root .. "/grokbot/hyprland/grokbot.lua")
assert(binds["SUPER + G"] == "special:grokbot", "SUPER+G missing")
assert(binds["SUPER + SHIFT + G"], "SUPER+SHIFT+G missing")
assert(rules[1][1] == "^(grok-bot)$" and rules[1][2].workspace == "special:grokbot silent")
assert(#unbinds == 2)
print("OK: Omarchy 4 Lua integration")
LUA
else
    echo 'SKIP: luac unavailable'
fi

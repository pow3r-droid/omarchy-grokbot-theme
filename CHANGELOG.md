# Changelog

## v1.1.0 — 2026-10-11

- Omarchy 4 support: Lua integration `grokbot/hyprland/grokbot.lua`, auto-loaded from the theme's `hyprland.lua` (no user config edit).
- Super+G panel on `special:grokbot` for class `grok-bot` (float, centered, 80%x70%); Super+Shift+G region screenshot to clipboard. Overrides the conflicting Omarchy defaults.
- Paths resolve via `~/.local/state/omarchy/current/theme` with fallback to `~/.config/omarchy/current/theme`.
- Legacy Omarchy 3 scratchpad now defaults to class `grok-bot`.
- Tests: Lua syntax check and stubbed load of the integration.
- README: Omarchy 4 section first; documents that the omarchy-shell bar does not take theme widgets.

## v1.0.0 — 2026-10-11

- Initial standalone Omarchy community-theme release with root-level app configs.
- Nine rotating 4K wallpapers (eight Grok Imagine images, one SpaceX launch photo via Unsplash), mission badge, and desktop preview.
- Optional Grok Bot scratchpad, Waybar module, screenshot binding, and helper CLI.
- Installation documentation and root-layout validation suite.

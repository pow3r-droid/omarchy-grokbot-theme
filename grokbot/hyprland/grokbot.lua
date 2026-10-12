-- Omarchi-Grokbot native integration for Omarchy 4 (Hyprland Lua config).
-- Loaded automatically by this theme's hyprland.lua; safe to dofile() manually.
-- Community theme, not affiliated with xAI, SpaceX or Omarchy.

local home = os.getenv("HOME") or ""
local class = os.getenv("GROKBOT_CLASS") or "grok-bot"

local function exists(path)
  local f = io.open(path, "r")
  if f then f:close() return true end
  return false
end

local function theme_dir()
  local candidates = {
    (os.getenv("XDG_STATE_HOME") or (home .. "/.local/state")) .. "/omarchy/current/theme",
    home .. "/.config/omarchy/current/theme",
  }
  for _, dir in ipairs(candidates) do
    if exists(dir .. "/grokbot/hyprland/grokbot.lua") then return dir end
  end
  return candidates[1]
end

local dir = theme_dir()
local screenshot = dir .. "/grokbot/waybar/grokbot-screenshot.sh"
local q = (o and o.shell_quote) or function(v) return "'" .. tostring(v):gsub("'", "'\\''") .. "'" end

-- Scratchpad window rules: Grok Bot lives on special:grokbot, floating and centered.
local match = "^(" .. class .. ")$"
o.window(match, {
  float = true,
  center = true,
  size = { "(monitor_w*0.8)", "(monitor_h*0.7)" },
  workspace = "special:grokbot silent",
})

-- Super+G toggles the Grok Bot panel (replaces Omarchy's default group toggle).
pcall(hl.unbind, "SUPER + G")
o.bind("SUPER + G", "Toggle Grok Bot panel", hl.dsp.workspace.toggle_special("grokbot"))

-- Super+Shift+G: region screenshot to clipboard (replaces default Signal launcher).
pcall(hl.unbind, "SUPER + SHIFT + G")
local shot_cmd
if exists(screenshot) then
  shot_cmd = "bash " .. q(screenshot)
else
  shot_cmd = "grim -g \"$(slurp)\" - | wl-copy --type image/png"
end
o.bind("SUPER + SHIFT + G", "Screenshot region for Grok Bot", shot_cmd)

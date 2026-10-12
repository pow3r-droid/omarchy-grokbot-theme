local active_border_color = "#4fd1ff"
local inactive_border_color = "rgba(595959aa)"

hl.config({
  general = {
    col = {
      active_border = active_border_color,
      inactive_border = inactive_border_color,
    },
  },

  group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },
  },
})

-- Omarchi-Grokbot integration (Omarchy 4). Guarded so a missing file or API
-- change never breaks Hyprland; set GROKBOT_DISABLE=1 to skip it.
if os.getenv("GROKBOT_DISABLE") ~= "1" then
  local home = os.getenv("HOME") or ""
  for _, dir in ipairs({
    (os.getenv("XDG_STATE_HOME") or (home .. "/.local/state")) .. "/omarchy/current/theme",
    home .. "/.config/omarchy/current/theme",
  }) do
    local path = dir .. "/grokbot/hyprland/grokbot.lua"
    local f = io.open(path, "r")
    if f then
      f:close()
      local ok, err = pcall(dofile, path)
      if not ok then print("grokbot: " .. tostring(err)) end
      break
    end
  end
end

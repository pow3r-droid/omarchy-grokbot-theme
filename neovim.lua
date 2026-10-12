-- Dependency-free palette, compatible with LazyVim's theme spec.
return {
  { "LazyVim/LazyVim", opts = { colorscheme = "default" }, init = function()
    -- Apply directly; no external colorscheme download is required.
    local function apply()
    vim.o.termguicolors = true

    vim.g.colors_name = "grokbot"
    local groups = {
      Normal = { fg = "#e6e6e6", bg = "#0a0a0b" },
      NormalFloat = { fg = "#e6e6e6", bg = "#16191c" },
      Comment = { fg = "#87919a", italic = true },
      Visual = { bg = "#24282c" },
      CursorLine = { bg = "#16191c" },
      LineNr = { fg = "#68727c" }, CursorLineNr = { fg = "#4fd1ff" },
      Function = { fg = "#ffffff" }, Keyword = { fg = "#4fd1ff" },
      String = { fg = "#b6bec6" }, Number = { fg = "#b6bec6" },
      DiagnosticError = { fg = "#ffffff", underline = true },
      DiagnosticWarn = { fg = "#4fd1ff" },
      FloatBorder = { fg = "#343a40" }, Search = { fg = "#000000", bg = "#4fd1ff" },
    }
    for group, spec in pairs(groups) do vim.api.nvim_set_hl(0, group, spec) end
    end
    vim.api.nvim_create_autocmd("ColorScheme", { callback = apply })
    apply()
  end },
}
